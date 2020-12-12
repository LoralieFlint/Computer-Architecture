"""CPU functionality."""

import sys
LDI = 0b10000010  # LDI R0,8
PRN = 0b01000111  # PRN R0
HLT = 0b00000001  # HLT
MUL = 0b10100010  # MUL R0,R1
PUSH = 0b01000101  # PUSH R0
POP = 0b01000110  # POP R0
CALL = 0b01010000  # CALL R1
RET = 0b00010001  # RET
ADD = 0b10100000  # ADD
# sprint
CMP = 0b10100111  # CMP
JEQ = 0b01010101  # JEQ
JMP = 0b01010100  # JMP
JNE = 0b01010110  # JNE


class CPU:
    """Main CPU class."""

    def __init__(self):
        """
        Construct a new CPU.
        """
        self.ram = [0] * 256

        self.reg = [0] * 8
        self.reg[7] = 0xf4

        self.sp = 7

        self.pc = 0

        self.flag = 0b00000000

        self.running = True

        self.branch_table = {
            LDI: self.new_ldi,
            PRN: self.new_prn,
            HLT: self.new_hlt,
            MUL: self.new_mul,
            PUSH: self.new_push,
            POP: self.new_pop,
            CALL: self.new_call,
            RET: self.new_ret,
            ADD: self.new_add,
            # sprint
            CMP: self.new_cmp,
            JEQ: self.new_jeq,
            JMP: self.new_jmp,
            JNE: self.new_jne
        }

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self, filename):
        """Load a program into memory."""
        try:
            with open(filename) as f:
                address = 0
                for line in f:
                    line = line.split('#')
                    num_str = line[0].strip()

                    if num_str == "":
                        continue
                    v = int(num_str, 2)
                    self.ram[address] = v
                    address += 1

        except FileNotFoundError:
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]

        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001  # HLT
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def new_ldi(self, reg_a, reg_b):
        self.reg[reg_a] = reg_b
        self.pc += 3

    def new_prn(self, reg_a, reg_b):
        print(f'Print this: {self.reg[reg_a]}')
        self.pc += 2

    def new_hlt(self, reg_a, reg_b):
        self.pc += 1
        self.running = False

    def new_mul(self, reg_a, reg_b):
        self.alu("MUL", reg_a, reg_b)
        self.pc += 3

    def new_add(self, reg_a, reg_b):
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3

    def new_push(self, reg_a, reg_b):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.reg[reg_a]
        self.pc += 2

    def new_pop(self, reg_a, reg_b):
        self.reg[reg_a] = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        self.pc += 2

    def new_call(self, reg_a, reg_b):
        return_add = self.pc + 2
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_add
        reg_num = self.ram[self.pc + 1]
        sub_add = self.reg[reg_num]
        self.pc = sub_add

    def new_ret(self, reg_a, reg_b):
        return_address = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        self.pc = return_address

    def new_cmp(self, reg_a, reg_b):
        self.alu("CMP", reg_a, reg_b)
        self.pc += 3

    def new_jeq(self, reg_a, reg_b):
        reg_num = self.ram_read(self.pc + 1)
        if self.flag & 0b00000001 == 1:
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def new_jmp(self, reg_a, reg_b): 
        reg_num = self.ram_read(self.pc + 1)
        self.pc = self.reg[reg_num]

    def new_jne(self, reg_a, reg_b):
        reg_num = self.ram_read(self.pc + 1)
        if self.flag & 0b00000001 == 0:
            self.pc = self.reg[reg_num]
        else:
            self.pc += 2

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram[self.pc]
            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)
            if ir in self.branch_table:
                self.branch_table[ir](reg_a, reg_b)

            else:
                print(f'Unknown instruction {ir} at address {self.pc}')
                sys.exit(1)
