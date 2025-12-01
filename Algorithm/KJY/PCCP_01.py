def solution(input_string):
    answer = ''
    tmp = ''
    dict = {}
    
    dict[input_string[0]] = 1
    
    for i in range(1, len(input_string)):
        if input_string[i] in dict:
            if input_string[i-1] != input_string[i]:
                if input_string[i] not in tmp:
                    tmp += input_string[i]
        else:
            dict[input_string[i]] = 1
                
    if tmp =='':
        answer = 'N'
    else:
        answer = ''.join(sorted(tmp))
    return answer