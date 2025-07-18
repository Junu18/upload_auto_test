def and_gate_verificate(and_gate): # 이자체가 파일 경로 with open 하면 되겠죠
    with open(and_gate, "r") as file:
        verilog_code = read.file()



    with open("and_gate.v", "r") as file:
        verilog_code =  file.read()

    inputs = []
    output = ""
    expression = ""


    lines = verilog_code.strip().splitlines()
    for line in lines:
        line = line.strip(";").strip()
        print(line)
        # if line[:6]module
        if line.startswith("module"): 
            # 시작하는 ()
            # 소괄호의 위치를 찾는  > 인덱스 번호를 알려준다.
            start  = line.find("(")
            end = line.find(")")
            parameter_section = line[start + 1:end]  # 슬라이싱은 끝부분 포함 X 
            # print(start,end)
            parameter_list= []

            for parameter in parameter_section.split(","):
                parameter_list.append(parameter.strip())
            # parameter_list  = parameter_section.split(",")
            
            for parameter in parameter_list:
                if parameter.startswith("input"):
                    inputs.append(parameter.replace("input", "").strip()) # input을 빈 문자열로 대체
                elif parameter.startswith("output"):
                    output = parameter.replace("output","").strip()
                else: 
                    if output == "":
                        inputs.append(parameter)
                # print("input :", inputs)                
                # print("output :", outputs)                
        elif line.startswith("assign"):
            # 사용자가 y를 체크를 한번더 조건을 걸고 해도 되지만 >> 보수적
            line = line.strip()
            # left = line.split("=")[0]  
            # 튜플로 받을 수 도 있다
            left, right = line.split("=")
            left = left.replace("assign", "").strip()
            # print(line.split("=")) # 라인을 = 기준으로 스플릿 , 공백도 고려하는게 코드와 일치 시키려고 하는듯
            right = right.strip()
            print(right)
            expression = f"{left.strip()}= {right.strip()}" # Verilog  a v => python 과 동작이 같을까? >> 같으니 문자열 그대로 저장 


    print("here :", expression)
            
    # 변수 ,표현식, output 구현        
            
    verilog_func = []
    verilog_func.append(f"def and_gate({','.join(inputs)}):")
    verilog_func.append(f"    {expression}")
    verilog_func.append(f"    return {output}")
    result = '\n'.join(verilog_func)
    exec(result)

    answer = 0
    
    try:

        if and_gate(0, 0)  == 0 :
            answer += 1
        if and_gate(1, 0)  == 0 :
            answer += 1
        if and_gate(1, 1)  == 1 :
            answer += 1
        
    except:
        return "모듈을 잘 못 설계하셨습니다."

    return f"정답률 : {answer/4 *100 : .0f}%"