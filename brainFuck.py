from colorama import init, Fore, Back, Style
import time, argparse

class MemoryBad(Exception):
	"""Pointer is out of memory range"""
	pass

class SyntaxBad(Exception):
	"""That's not allowed >:("""
	pass

def parse(code):
	accepted = "+-[]<>.,"
	parsedCode = ""

	for char in code:
		if char in accepted:
			parsedCode += char

	return parsedCode


def validate(code):
	if not code.count("[") == code.count("]"):
		raise SyntaxBad("Unequal bracket amount")


def findBracket(code, start=None, end=None):
	layer = 0
	if start:
		# find closing bracket
		for i, c in enumerate(code[start+1:]):
			if c == "]":
				if not layer:
					return len(code[:start+1]) + i
				else:
					layer -= 1

			elif c == "[":
				layer += 1

	elif end:
		# find opening bracket
		for i, c in enumerate(code[:end][::-1]):
			if c == "[":
				if not layer:
					return end - (i+1)
				else:
					layer -= 1

			elif c == "]":
				layer += 1


def interpret(code, config):
	memory = [0 for i in range(1_000)]
	pointer = 0
	cmdTracker = [] # for visualization
	output = ""

	code = parse(code)
	validate(code)

	# to allow the compiler to skip code using []
	cursor = 0
	while cursor < len(code):
		c = code[cursor]

		# arithmatic
		if c == "+":
			if memory[pointer] == 255:
				memory[pointer] = 0
			else:
				memory[pointer] += 1

		elif c == "-":
			if memory[pointer] == 0:
				memory[pointer] = 255
			else:
				memory[pointer] -= 1

		# pointer shifting
		elif c == "<":
			if pointer - 1 >= 0:
				pointer -= 1
			else:
				raise MemoryBad("Pointing out of memory range")

		elif c == ">":
			if pointer + 1 < len(memory):
				pointer += 1
			else:
				raise MemoryBad("Pointing out of memory range")

		# loops
		elif c == "[":
			if memory[pointer] == 0:
				cursor = findBracket(code, start=cursor)

		elif c == "]":
			if memory[pointer] != 0:
				cursor = findBracket(code, end=cursor)

		# IO
		elif c == ".":
			output += chr(memory[pointer])

		elif c == "," and not config["visualize"]:
			memory[pointer] = ord(input("input: ")[0])




		if config["visualize"]:
			cmdTracker.append(render(memory, pointer, config))
		
		cursor += 1

	if config["visualize"]:
		renderVisualFrame(cmdTracker, output, config)

	else:
		print("\n" + render(memory, pointer, config) + f"\nOutput: {output}\n")


def renderVisualFrame(cmdTracker, output, config):
	print()
	for i, ins in enumerate(cmdTracker):
		bsCount = config["renderAmount"]*2 + config["renderAmount"]
		print("\b"*bsCount + ins, end="")

		if not i == len(cmdTracker) - 1:
			time.sleep(config["delay"])

	print(" : " + output + "\n")


def render(memory, pointer, config):
	string = ""
	for k, v in enumerate(memory[:config["renderAmount"]]):
		if k == pointer:
			string += f"{Back.CYAN}{v}{Style.RESET_ALL} "
		else:
			string += str(v) + " "

	return string


def main(code, config):
	init()
	#code = "duplicate pointer to the next cell:+++  [->+>+<<]>>[-<<+>>] <<"

	if code:
		interpret(code, config)
	else:
		while True:
			interpret(input("code: "), config)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-c", "--code", help="Brainfuck code to be executed")
	parser.add_argument("-v", "--visualize", help="Print the visualization", type=lambda i: "true" in i.lower(), default=False)
	parser.add_argument("-d", "--delay", help="Delay in seconds (visualize mode)", type=float, default=0.05)
	parser.add_argument("-l", "--length", help="Amount of memory cells to render", type=int, default=10)

	args = parser.parse_args()
	main(args.code, {"visualize": args.visualize, "delay": args.delay, "renderAmount": args.length})