# Mock ASM Runtime

:no_entry: [DEPRECATED] in favour of https://github.com/yamini-vm/yamini.

A simple assembler for a mock instruction set along with a runtime to run the resulting code.

## Installation

```bash
user@programmer~:$ pip install git+https://github.com/frankhart2018/mockasm-runtime.git
```

**Note**:- I do not plan in pushing this to pypi anytime soon (or maybe ever).

## Usage

```bash
user@programmer~:$ mockasm --file_path test.s
```

## Debugging

### Generate tokens

```bash
user@programmer~:$ mockasm --file_path test.s --tokens
```

### Generate opcodes

```bash
user@programmer~:$ mockasm --file_path test.s --opcodes
```

### Generate both tokens and opcodes

```bash
user@programmer~:$ mockasm --file_path test.s --tokens --opcodes
```

**Note**:- The order in which you specify the flags (--tokens, --opcodes) does not matter.
