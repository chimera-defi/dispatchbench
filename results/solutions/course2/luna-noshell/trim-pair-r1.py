def findOrder(numCourses: int, prerequisites: list[list[int]]) -> list[int]:
    graph = [[] for _ in range(numCourses)]
    indegree = [0] * numCourses

    for course, prerequisite in prerequisites:
        graph[prerequisite].append(course)
        indegree[course] += 1

    ready = [course for course in range(numCourses) if indegree[course] == 0]
    order = []

    while ready:
        course = ready.pop()
        order.append(course)
        for next_course in graph[course]:
            indegree[next_course] -= 1
            if indegree[next_course] == 0:
                ready.append(next_course)

    return order if len(order) == numCourses else []
