"""Rerun every retained Codex cell without changing historical caches/results.

python3 -m bench.isolated --track all --dry-run --parity
python3 -m bench.isolated --track function --max-calls 5

Counts are result attempts; rescue attempts share builds/plans and can make
conditional repair calls. --max-calls caps actual uncached model invocations
(including Claude pipeline steps), separately for each track. main/hard remain
aliases for the original two ablation cells; all uses the complete function track.
"""
import argparse
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shlex
import sys
import threading

from bench import grade, grade_all, run, plan_first, gated_repair, trim_probe
from bench.agentic import run as agentic

TRACKS = ('function', 'agentic', 'harness_bias', 'rescue')
# Historical key material, independent of the current runner's flags/configs.
OLD_FLAGS = ['--ignore-user-config', '-c', 'skills.include_instructions=false',
             '-c', 'service_tier=default', '--json', '--ephemeral',
             '--skip-git-repo-check', '-s', 'read-only']
OLD_CLAUDE_FLAGS = ['--output-format', 'json', '--no-session-persistence',
                    '--tools', '', '--setting-sources', '', '--strict-mcp-config']
OLD_MODELS = {'luna': 'gpt-6-luna', 'sol61': 'gpt-6.1-sol',
              'sol56': 'gpt-5.6-sol', 'luna56': 'gpt-5.6-luna', 'astra': 'gpt-6-astra'}


def read(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines()] if Path(path).exists() else []


def plans():
    root = Path(run.ROOT) / 'results'
    return {
        'function': [r for r in read(root / '2026-10-22b-function.jsonl')
                     if r['cli'] == 'codex' and r['phase'] != 'warmup'],
        'agentic': [r for r in read(root / '2026-10-22b-agentic.jsonl') if r['cli'] == 'codex'],
        'harness_bias': [r for r in read(root / 'appendix/harness_bias.jsonl')
                         if r['cli'] == 'codex' and r['harness'] == 'claude-one-shot'],
        'rescue': [r for r in read(root / 'appendix/luna_rescue.jsonl') if r['arm'] in ('F', 'G')],
    }


def digest(blob):
    return hashlib.sha256(json.dumps(blob, sort_keys=True).encode()).hexdigest()


def settings(track, config, portable=False):
    if track == 'rescue':
        mid, effort, flags = (plan_first.BUILDERS[config] if config in plan_first.BUILDERS
                              else gated_repair.CONFIGS[config][:3])
    else:
        _, mid, effort = run.CONFIGS[config]
        flags = agentic.CODEX_FLAGS if track == 'agentic' else run.codex_flags(config, portable=portable)
    return mid, effort, list(flags)


def normalized(flags):
    return ['model_instructions_file=<MIN_INST>' if f.startswith('model_instructions_file=') else f for f in flags]


def old_settings(track, row):
    """Recover settings by reproducing recorded keys (never run a CLI)."""
    config = row['config']
    if track == 'rescue':
        builder = config.split('+')[-1] if row['arm'] == 'F' else config.split('+')[0]
        family, effort, *_ = builder.split('-')
        mid = OLD_MODELS[family]
    else:
        mid, effort = row['model'], row['effort']
    base = OLD_FLAGS.copy()
    if track == 'agentic':
        base[-1] = 'workspace-write'
    bare = '-bare' in config
    for tier in ('default', 'priority'):
        flags = [f'service_tier={tier}' if x == 'service_tier=default' else x for x in base]
        if bare:
            flags += trim_probe.LEVELS['noshell']
        if track == 'rescue':
            # Old pipeline keys held an absolute instruction-file path.
            flags = [x.replace('<MIN_INST>', json.dumps('/home/agents/workspace/model-routing-bench/bench/pilot/min_instructions.txt')) for x in flags]
            blob = dict(model=mid, effort=effort, cli=row['codex_cli'], flags=flags,
                        prompt=run.prompt_for(row['problem']), repeat=row['repeat'])
            module = gated_repair
            if row['arm'] == 'F':
                module = plan_first
                m = run.problems.load(row['problem'])
                plan_blob = dict(model=('claude-haiku-5-5', 'low'), cli=row['claude_cli'],
                                 flags=OLD_CLAUDE_FLAGS, repeat=row['repeat'],
                                 prompt=module.PLAN.format(statement=m.STATEMENT.strip(), signature=m.SIGNATURE))
                plan_path = Path(run.ROOT) / 'cache/plan_first' / f'plan-{digest(plan_blob)}.json'
                if not plan_path.exists(): continue
                pl = json.loads(plan_path.read_text())
                blob.update(config=config, prompt=module.BUILD.format(prompt=blob['prompt'], plan=pl['text'].strip()))
            path = Path(run.ROOT) / 'cache' / ('plan_first' if row['arm'] == 'F' else 'gated_repair') / f'build-{digest(blob)}.json'
            if path.exists():
                return mid, effort, normalized(flags)
        else:
            blob = {k: row[k] for k in ('config', 'cli', 'model', 'effort', 'cli_version', 'repeat')}
            blob.update(flags=flags)
            if track == 'agentic':
                task = Path(agentic.TASKS) / row['task']
                blob.update(track='agentic', task=row['task'], prompt=(task / 'TASK.md').read_text(),
                            task_tree=agentic.tree_hash(str(task / 'repo'), str(task / 'hidden')))
            else:
                blob.update(problem=row['problem'], prompt=run.prompt_for(row['problem']))
            if digest(blob) == row['key']:
                if row.get('service_tier', tier) != tier or ('flags' in row and normalized(row['flags']) != normalized(flags)):
                    raise ValueError('recorded fields conflict with cache key')
                return mid, effort, normalized(flags)
    raise ValueError('historical cache key could not be reproduced')


def parity(track, rows, emit=True):
    groups = defaultdict(list)
    for row in rows: groups[row['config']].append(row)
    passed = True
    for config, rr in sorted(groups.items()):
        new = settings(track, config)
        try:
            old = {json.dumps(old_settings(track, r)) for r in rr}
            expected = json.dumps((new[0], new[1], normalized(new[2])))
            ok = old == {expected}
            if '-bare' in config:
                ok = ok and hashlib.sha256(Path(trim_probe.MIN_INST).read_bytes()).hexdigest() == trim_probe.MIN_INST_SHA
            if track == 'rescue':
                module = plan_first if rr[0]['arm'] == 'F' else gated_repair
                ok = ok and module.CLAUDE_FLAGS == OLD_CLAUDE_FLAGS
            description = ' | '.join(sorted(old))
        except (KeyError, ValueError, OSError) as exc:
            ok, description = False, str(exc)
        passed &= ok
        if emit:
            argv = [run.CODEX, 'exec', '-m', new[0], '-c', f'model_reasoning_effort={new[1]}', *new[2], '-C', '<isolated-work>', '<task prompt>']
            phases = ','.join(sorted({r.get('phase', 'rescue '+r['arm'] if 'arm' in r else track) for r in rr}))
            print(f"{'OK' if ok else 'MISMATCH'} {track}/{config} [{phases}] old(model,effort,flags)={description}; trim={'noshell' if '-bare' in config else 'stock'}; new argv={shlex.join(argv)}")
    return passed


class CallLimit(RuntimeError):
    pass


class CallBudget:
    def __init__(self, maximum):
        self.maximum, self.used = maximum, 0
        self.lock = threading.Lock()

    def wrap(self, call):
        def bounded(*args, **kwargs):
            with self.lock:
                if self.maximum is not None and self.used >= self.maximum:
                    raise CallLimit('max-calls reached')
                self.used += 1
            return call(*args, **kwargs)
        return bounded


@contextmanager
def overrides(changes):
    saved = [(module, key, getattr(module, key)) for module, key, _ in changes]
    try:
        for module, key, value in changes: setattr(module, key, value)
        yield
    finally:
        for module, key, value in reversed(saved): setattr(module, key, value)


def row_id(r):
    return (r['config'], r.get('phase'), r.get('arm'), r.get('harness'), r.get('problem', r.get('task')), r['repeat'])


def write_rows(output, rows):
    old = {row_id(r): r for r in read(output)}
    old.update((row_id(r), r) for r in rows)
    output.parent.mkdir(exist_ok=True)
    tmp = output.with_suffix('.jsonl.tmp')
    tmp.write_text(''.join(json.dumps(r) + '\n' for r in old.values()))
    tmp.replace(output)


def execute(track, rows, output, lanes, maximum):
    output.parent.mkdir(parents=True, exist_ok=True)
    cache = Path(run.ROOT) / 'cache/isolated'
    budget = CallBudget(maximum)
    changes = [(run, 'CALLS', str(cache / 'calls')), (run, 'RAW', str(cache / 'raw')),
               (agentic, 'RAW', str(cache / 'raw')), (agentic, 'CACHE', str(cache / 'agentic')),
               (agentic, 'PATCHES', str(cache / 'agentic_patches')),
               (grade_all, 'GRADES', str(cache / 'grades')), (grade, 'EXPECTED_DIR', str(cache / 'expected')),
               (plan_first, 'CACHE', str(cache / 'plan_first')), (gated_repair, 'CACHE', str(cache / 'gated_repair'))]
    for module, names in ((run, ('call_codex', 'call_claude')), (agentic, ('run_codex', 'run_claude')),
                          (plan_first, ('call_codex', 'call_claude')), (gated_repair, ('call_codex', 'call_claude'))):
        changes += [(module, name, budget.wrap(getattr(module, name))) for name in names]
    groups = defaultdict(list)
    for row in rows: groups[row['config']].append(row)
    completed = []
    export_lock = threading.Lock()
    with overrides(changes):
        Path(grade_all.GRADES).mkdir(parents=True, exist_ok=True)
        def lane(jobs):
            for r in jobs:
                c, rep = r['config'], r['repeat']
                try:
                    if track == 'rescue':
                        module = plan_first if r['arm'] == 'F' else gated_repair
                        result = dict(module.one(c, r['problem'], rep), codex_home='isolated')
                        with export_lock: write_rows(output, [result])
                    elif track == 'agentic':
                        msg = agentic.one(c, r['task'], rep, lanes, regrade=True)
                        if msg.startswith(('refused', 'stopped')): return
                    else:
                        msg = run.one(c, r['problem'], rep, r['phase'], lanes)
                        if msg.startswith(('refused', 'stopped')): return
                    with export_lock: completed.append(r)
                except CallLimit:
                    return
        # Pipeline caches share plans/builds; serialize them to avoid duplicate misses.
        with ThreadPoolExecutor(1 if track == 'rescue' else lanes) as pool:
            list(pool.map(lane, groups.values()))
        if track == 'agentic':
            keys = {agentic.key_for(r['config'], r['task'], r['repeat']) for r in completed}
            selected = [r for p in Path(agentic.CACHE).glob('*.json')
                        if (r := json.loads(p.read_text()))['key'] in keys]
            write_rows(output, selected)
        elif track != 'rescue':
            entries = []
            for r in completed:
                key = run.key_for(r['config'], r['problem'], r['repeat'], run.prompt_for(r['problem']))
                entry = json.loads((Path(run.CALLS) / f'{key}.json').read_text())
                entries.append(dict(entry, phase=r['phase']))
            temporary = output.with_suffix('.graded.tmp')
            grade_all.main(entries=entries, output=str(temporary))
            selected = read(temporary)
            temporary.unlink()
            for r in selected:
                if track == 'harness_bias':
                    from analysis.harness_bias import fill_cost
                    r['harness'] = 'claude-one-shot'
                    fill_cost(r)
            write_rows(output, selected)
    print(f'[{track}] completed {len(completed)} attempts; {budget.used} uncached model calls')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--track', choices=('all', 'main', 'hard', *TRACKS), default='all')
    ap.add_argument('--dry-run', action='store_true', help='print plan without CLI or API calls')
    ap.add_argument('--parity', action='store_true', help='verify old cache identities against new argv (requires --dry-run)')
    ap.add_argument('--max-calls', type=int, default=None, help='maximum uncached model invocations per track, including pipeline steps')
    ap.add_argument('--lanes', type=int, choices=range(1, 5), default=4)
    ap.add_argument('--reps', type=int, default=0, help='first N recorded repeats per cell (0 = all)')
    ap.add_argument('--agentic-tasks', default='all')
    a = ap.parse_args(argv)
    if a.parity and not a.dry_run: ap.error('--parity requires --dry-run')
    if a.reps < 0 or (a.max_calls is not None and a.max_calls < 0): ap.error('call/repeat limits must be nonnegative')
    tasks = agentic.TASK_IDS if a.agentic_tasks == 'all' else a.agentic_tasks.split(',')
    if not tasks or len(tasks) != len(set(tasks)) or any(t not in agentic.TASK_IDS for t in tasks):
        ap.error('--agentic-tasks must contain distinct known task IDs')
    plan = plans()
    if a.track in ('main', 'hard'):
        config = 'luna-low' if a.track == 'main' else 'sol61-high'
        plan = {a.track: [r for r in plan['function'] if (r['config'], r['phase']) == (config, a.track)]}
    elif a.track != 'all': plan = {a.track: plan[a.track]}
    total, ok = 0, True
    for track, rows in plan.items():
        if track == 'agentic': rows = [r for r in rows if r['task'] in tasks]
        if a.reps:
            repeats = defaultdict(set)
            for r in rows: repeats[(r['config'], r.get('phase'), r.get('arm'))].add(r['repeat'])
            rows = [r for r in rows if r['repeat'] in sorted(repeats[(r['config'], r.get('phase'), r.get('arm'))])[:a.reps]]
        total += len(rows)
        output = Path(run.ROOT) / 'results' / f'2026-10-25-isolated-{track}.jsonl'
        print(f'[isolated/{track}] {len(rows)} calls (result attempts); results: {output.name}', flush=True)
        if a.max_calls is not None: print(f'Uncached model call limit: {a.max_calls}')
        kind = 'function' if track in ('main', 'hard') else track
        if a.dry_run:
            if a.parity: ok = parity(kind, rows) and ok
            else:
                for c in sorted({r['config'] for r in rows}):
                    mid, effort, flags = settings(kind, c)
                    print(shlex.join([run.CODEX, 'exec', '-m', mid, '-c', f'model_reasoning_effort={effort}', *flags]))
        else:
            execute(kind, rows, output, a.lanes, a.max_calls)
    print(f'Total: {total} calls (result attempts)')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
