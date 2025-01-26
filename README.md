# 🖥️ RISC-V 32-bit Assembler and Simulator

This project implements a **three-pass assembler** and **simulator** for the RISC-V 32-bit integer ISA. It is designed to handle a wide range of operations including register operations, memory management, conditionals, and function calls.

The assembler converts assembly code into machine code, while the simulator executes the machine code, showcasing register changes and the final memory state.

---

## ✨ Features

### 🛠️ Assembler

- **Three-pass design:**
  - 🔍 **Pass 1:** Symbol table generation and error detection.
  - 📦 **Pass 2:** Instruction encoding and address resolution.
  - ✅ **Pass 3:** Machine code output generation and verification.
- Supports standard RISC-V instructions for 32-bit integer operations. 📝
- Handles directives, labels, and pseudo-instructions. 🏷️
- Provides detailed error messages for syntax and semantic issues. ⚠️

### 🚀 Simulator

- Executes the generated machine code. 🏃‍♂️
- Displays:
  - 📊 Register states after each instruction.
  - 🗂️ Final memory state after program execution.
- Implements:
  - ➕ Arithmetic and logical operations.
  - 💾 Load and store instructions for memory management.
  - 🔄 Conditional branching and jumps.
  - 📞 Function call and return mechanisms.
