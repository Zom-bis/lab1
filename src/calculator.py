
x='5 + 8 * 3 -12 / 6'
num='0123456789'
oper='+-*/'
prior={'+':'0','-':'0','*':'1','/':'1'}
def machine_code(inp):
    new_code=['']
    o=[]
    i=0
    q=0
    for s1 in range(len(inp)):
        s=inp[s1]

        if s in num or (s in '+-' and q==2 and inp[s1+1]in num) or (s in '+-' and q==0  and inp[s1+1]in num):
            if q==2:
                i+=1
                new_code += ' '
            new_code[i]=new_code[i]+s
            q=1
        elif s in oper:
            while len(o)>0:

                if prior[o[-1]][0]>=prior[s][0]:
                    new_code+=[o[-1]]
                    i+=1
                    o.remove(o[-1])
                    q=2
                else:
                    q=2
                    break
            q=2
            o+=s


    for x in o[::-1]: new_code+=x

    return new_code
res=machine_code(x)
p=[int(prior[x][0]) for x in res if x in oper]


while len(p)>0:
    mx=max(p)
    res1=[]
    for x in range(len(res)):
        s=res[x]

        if s in oper and prior[s][0]==str(mx):
            if s=='*':
                a=int(res1[-2])*int(res1[-1])
                res1.remove(res1[-2])
                res1.remove(res1[-1])
                res1.append(str(a))
                p.remove(max(p))
            elif s == '-':
                a = int(res1[-2]) - int(res1[-1])
                res1.remove(res1[-2])
                res1.remove(res1[-1])
                res1.append(str(a))
                p.remove(max(p))
            elif s == '+':
                a = int(res1[-2]) + int(res1[-1])
                res1.remove(res1[-2])
                res1.remove(res1[-1])
                res1.append(str(a))
                p.remove(max(p))
            elif s == '/':
                a = int(res1[-2]) // int(res1[-1])
                res1.remove(res1[-2])
                res1.remove(res1[-1])
                res1.append(str(a))
                p.remove(max(p))
        else:
            res1.append(s)
    res=res1

print(res1)
    
      
      
