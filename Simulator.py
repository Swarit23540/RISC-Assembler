import sys

Registers = {
    "zero": "00000", "ra": "00001", "sp": "00010", "gp": "00011", "tp": "00100",
    "t0": "00101", "t1": "00110", "t2": "00111", "s0": "01000", "s1": "01001",
    "a0": "01010", "a1": "01011", "a2": "01100", "a3": "01101", "a4": "01110",
    "a5": "01111", "a6": "10000", "a7": "10001", "s2": "10010", "s3": "10011",
    "s4": "10100", "s5": "10101", "s6": "10110", "s7": "10111", "s8": "11000",
    "s9": "11001", "s10": "11010", "s11": "11011", "t3": "11100", "t4": "11101",
    "t5": "11110", "t6": "11111"
}

# Initialize the register values
register_data= {i: '0'*32 for i in Registers.keys()}
register_data['sp'] = '0'*23 + '100000000'

# Reverse the Registers dictionary
Registers = {val:key for key,val in Registers.items()}

# Data memory initialization
memory={hex(0x0001_0000 + i*4):'00000000000000000000000000000000' for i in range(32)}

# R-Type Instructions
R_type = {'add':['0000000','000','0110011'],'sub':['0100000','000','0110011'],'sll':['0000000', '001', '0110011'],'slt':['0000000','010','0110011'],
    'sltu':['0000000', '011', '0110011'],'xor':['0000000','100','0110011'],'srl':['0000000', '101', '0110011'],'or':['0000000', '110', '0110011'],
    'and':['0000000', '111', '0110011']
}
R_type_reversed={tuple(value): key for key, value in R_type.items()}

# I-Type Instructions
I_type = {'lw':['010', '0000011'],'addi':['000', '0010011'],'sltiu':['011','0010011'],'jalr':['000','1100111']}

# B-Type Instructions
B_type={'beq':['000','1100011'],'bne':['001','1100011'],'blt':['100','1100011'],'bge':['101','1100011'],'bltu': ['110','1100011'],'bgeu':['111', '1100011']}

def twos_complement(n,size):
    if n>=0:
        binary=bin(n)[2:].zfill(size)
        return binary
    binary=bin(abs(n))[2:]  
    binary=binary.zfill(size)
    inverted_binary=''.join('1' if bit=='0' else '0' for bit in binary)
    inverted_binary=bin(int(inverted_binary, 2) + 1)[2:] 
    return inverted_binary.zfill(size)

def cal_2s_complement(binary):
    inverted=''.join('1' if bit=='0' else '0' for bit in binary)
    carry=1
    result=''
    for bit in inverted[::-1]:
        if bit=='0' and carry==1:
            result='1'+result
            carry=0
        elif bit=='1' and carry==1:
            result='0'+result
            carry=1
        else:
            result=bit+result
    return result

def execute_R(inst,register_data):
    funct7=inst[0:7]
    funct3=inst[17:20]
    opcode='0110011'
    op=R_type_reversed[(funct7, funct3, opcode)]
    rs2=register_data[Registers[inst[7:12]]]
    rs1=register_data[Registers[inst[12:17]]]
    rd=Registers[inst[20:25]]
    
    operations={
        'add':lambda b,c:bin(int(b,2)+int(c,2))[2:].zfill(32),
        'slt':lambda b,c:'0'*31+'1' if int(b,2)<int(c,2) else '0'*32,
        'sltu':lambda b,c:'0'*31+'1' if int(b,2)<int(c,2) else '0'*32,
        'xor':lambda b,c:bin(int(b,2)^int(c,2))[2:].zfill(32),
        'or':lambda b,c:bin(int(b,2)|int(c,2))[2:].zfill(32),
        'and':lambda b,c:bin(int(b,2)&int(c,2))[2:].zfill(32),
        'sub':lambda b,c:bin(int(b,2)-int(c,2))[2:].zfill(32),
        'sll':lambda b,c:bin((int(c,2)<<int(b[27:32], 2)))[2:].zfill(32),
        'srl':lambda b,c:bin((int(c,2)>>int(b[27:32],2))&0xFFFFFFFF)[2:].zfill(32)
    }

    register_data[rd]=operations[op](rs2,rs1)
    
    return register_data

def execute_U(inst,register_data,pc):
    rd=Registers[inst[20:25]]
    imm=(inst[:20])
    if imm[0]=='1':
        imm=cal_2s_complement(imm)
        imm=-int(imm,2)
    else:
        imm=int(imm,2)

    opcode=inst[25:32]
    
    if opcode=='0110111':  # lui
        register_data[rd]=bin(imm<<12)[2:].zfill(32)
    elif opcode=='0010111':  # auipc
        register_data[rd]=bin(int(pc,2)+(imm<<12))[2:].zfill(32)

    return register_data

def execute_I(inst,register_data,pc):
    rs1=register_data[Registers[inst[12:17]]]
    rd=Registers[inst[20:25]]
    imm=inst[0:12]
    
    if imm[0]=='1':
        imm=cal_2s_complement(imm)
        imm=-int(imm,2)
    else:
        imm=int(imm,2) 

    opcode=inst[25:32]
    if opcode=='0000011':  # lw
        mem_address=bin(int(rs1,2)+imm)[2:].zfill(32)
        register_data[rd]=memory[hex(int(mem_address,2))]
        return register_data,pc
    elif opcode=='1100111':  # jalr
        register_data[rd]=twos_complement(int(pc,2)+4,32)
        new_pc=twos_complement(int(rs1,2)+imm,32)
        new_pc=new_pc[:-1] + '0'

        return register_data,new_pc
    elif inst[17:20]=='000':  # addi
        register_data[rd]=twos_complement(int(rs1,2)+imm,32)
        return register_data, pc
    else:  # sltiu
        register_data[rd]='0'*31+'1' if int(rs1, 2)<imm else '0'*32
        return register_data,pc

def execute_J(inst,register_data,pc):
    imm=inst[0]+inst[12:20]+inst[11]+inst[1:11]+'0'
    if imm[0]=='1':
        imm=cal_2s_complement(imm)
        imm=-int(imm,2)
    else:
        imm=int(imm,2)   
    
    rd=Registers[inst[20:25]]
    register_data[rd]=twos_complement(int(pc,2)+4,32)
    pc=twos_complement(int(pc,2)+imm,32)
    return register_data,pc

def execute_S(inst,register_data):
    imm=(inst[0:7]+inst[20:25])
    if imm[0]=='1':
        imm=cal_2s_complement(imm)
        imm=-int(imm,2)
    else:
        imm=int(imm,2)  
    rs2=Registers[inst[7:12]]
    rs1=register_data[Registers[inst[12:17]]]
    mem_address=twos_complement(int(rs1,2)+imm,32)
    memory[hex(int(mem_address, 2))]=register_data[rs2]
    return register_data


def execute_B(inst,register_data,pc):
    imm=inst[0]+inst[24]+inst[1:7]+inst[20:24]+'0'
    
    if imm[0]=='1':
        imm=cal_2s_complement(imm)
        imm=-int(imm,2)
    else:
        imm=int(imm,2)
    
    rs1=register_data[Registers[inst[12:17]]]
    rs2=register_data[Registers[inst[7:12]]]
    
    funct3 = inst[17:20]
    B_operaation={
        '000':lambda a,b:a==b,  # beq
        '001':lambda a,b:a!=b,  # bne
        '100':lambda a,b:int(a,2)<int(b,2),  # blt
        '101':lambda a,b:int(a,2)>=int(b,2),  # bge
        '110':lambda a,b:int(a,2)<int(b,2),  # bltu
        '111':lambda a,b:int(a,2)>=int(b,2)  # bgeu
    }
    
    if B_operaation[funct3](rs2, rs1):
        new_pc=twos_complement(int(pc,2)+imm,32)
    else:
        new_pc=bin(int(pc,2)+4)[2:].zfill(32)
    return new_pc

def get_file_paths():
    file_path = sys.argv[1]
    output_path = sys.argv[2]
    return file_path, output_path

def execute_instruction(instruction,pc):
    global register_data
    opcode=instruction[25:32]
    if opcode=='0110011':
        register_data=execute_R(instruction,register_data)
        pc=bin(int(pc,2)+4)[2:].zfill(32)
    elif opcode in ['0110111','0010111']:
        register_data=execute_U(instruction,register_data,pc)
        pc=bin(int(pc,2)+4)[2:].zfill(32)
    elif opcode in ['0000011','0010011','1100111']:
        register_data,pc=execute_I(instruction,register_data,pc)
        if opcode!='1100111':
            pc=bin(int(pc, 2)+4)[2:].zfill(32)
    elif opcode=='1101111':
        register_data,pc=execute_J(instruction,register_data,pc)
    elif opcode=='0100011':
        register_data=execute_S(instruction, register_data)
        pc = bin(int(pc,2)+4)[2:].zfill(32)
    elif opcode=='1100011':
        pc=execute_B(instruction,register_data,pc)
    return register_data,pc

def write(w,pc,register_data,memory):
    w.write('0b'+pc+ ' ')
    for i in register_data:
        w.write('0b'+register_data[i] +' ')
    w.write('\n')
    for address, value in memory.items():
        w.write('0x'+format(int(address, 16),'08x')+':0b'+value+'\n')

def main():
    file_path,output_path=get_file_paths()
    with open(file_path,'r') as f:
        instructions=f.readlines()
        register_data={i:'0'*32 for i in Registers.keys()}
        pc='0'*29+'000'
        with open(output_path,'w') as w:
            while instructions[int(pc,2)//4]!='00000000000000000000000001100011':
                instruction = instructions[int(pc,2)//4]
                if instruction=='00000000000000000000000001100011\n':
                    break
                register_data,pc=execute_instruction(instruction,pc)
                register_data['zero']='0'*32

                w.write('0b'+pc+' ')
                for i in register_data:
                    w.write('0b'+register_data[i]+' ')
                w.write('\n')
            write(w,pc,register_data,memory)
            print("done")

main()
