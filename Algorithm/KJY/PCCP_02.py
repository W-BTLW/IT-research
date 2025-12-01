def dfs(x, cnt, ability, visited):
    global answer
    n = len(ability)
    game = len(ability[0])
    
    if x == game:
        if answer < cnt:
            answer = cnt
            return
    else:
        for i in range (n):
            if visited[i] == 0:
                visited[i] = 1
                dfs(x+1, cnt+ability[i][x], ability, visited)
                visited[i] = 0

def solution(ability):
    global answer
    answer = 0
    visited = [0] * len(ability)
    dfs(0, 0, ability, visited)
    return answer