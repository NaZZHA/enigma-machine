alphabet = [chr(i) for i in range(97, 123)]


class rotor:
	def __init__(self, shift, f=False):
		self.default_shift = shift % 26
		self.shift_value = shift % 26
		self.shift_inverse = -shift
		self.next_rotor = None
		self.prev_rotor = None
		self.start = False
		self.last = True
		self.stored_value = 0

	def update_next_rotor(self, other):
		self.next_rotor = other
		other.prev_rotor = self
		self.last = False
		other.start = False

		if self.prev_rotor:
			self.start = True

	def update_shift(self):
		self.shift_value += 1
		if self.shift_value % 26 == 0:
			if self.next_rotor:
				self.next_rotor.update_shift()
			self.shift_value == 0

	def transform(self, let):
		return alphabet.index(let) + 1

	def foward_pass(self, value):
		if type(value) is str:
			value = self.transform(value)

		v = (value + self.shift_value) % 26

		if self.last == False:
			self.next_rotor.foward_pass(v)

		#self.stored_value = v
		self.backward_pass(v)

	def backward_pass(self, value):
		v = value
		v = (value + self.shift_value) % 26

		if self.prev_rotor:
			self.prev_rotor.backward_pass(v)

		#print(f'{value} + {self.shift_value} = {v}')
		self.stored_value = v

	def inverse_foward_pass(self, value):
		if type(value) is str:
			value = self.transform(value)

		v = (value - self.shift_value) % 26

		if self.last == False:
			self.next_rotor.inverse_foward_pass(v)

		#self.stored_value = v
		self.inverse_backward_pass(v)

	def inverse_backward_pass(self, value):
		v = value
		v = (value - self.shift_value) % 26

		if self.prev_rotor:
			self.prev_rotor.inverse_backward_pass(v)

		self.stored_value = v		

	def get_result(self):
		return self.stored_value

	def clear(self):
		self.stored_value = 0

	def reset_all(self):
		self.shift_value = self.default_shift
		if self.next_rotor:
			self.next_rotor.reset_all()


class machine:
	def __init__(self, *shifts):
		self.rotors = []
		self.plugboard = {}
		for i in shifts:
			self.rotors.append(rotor(i))

		for i in self.rotors:
			if self.rotors.index(i) == 0:
				continue

			self.rotors[self.rotors.index(i) - 1].update_next_rotor(i)

	def set_plugboard(self, new_vals):
		for x, y in zip(alphabet, list(new_vals)):
			self.plugboard[x] = y

	def add_rotor(self, shift):
		self.rotors.append(rotor(shift))
		if not self.rotors:
			self.rotors[-2].update_next_rotor(self.rotors[-1])

	def encrypt(self, code, use_plugboard=True):
		self.rotors[0].reset_all()
		y = []

		for i in code:
			x = i.lower()
			if not x in alphabet:
				if i == '.':
					self.rotors[0].reset_all()
				y.append(i)
				continue

			if use_plugboard == True and self.plugboard:
				x = self.plugboard[x]

			self.rotors[0].foward_pass(x)
			self.rotors[0].update_shift()
			y.append(alphabet[self.rotors[0].stored_value - 1])

		return ''.join(y)

	def get_inverse_letter(self, let):
		for x, y in self.plugboard.items():
			if y == let:
				return x

	def decrypt(self, code, use_plugboard=True):
		self.rotors[0].reset_all()
		y = []

		for i in code.strip():
			x = i.lower()

			if not x in alphabet:
				if i == '.':
					self.rotors[0].reset_all()
				y.append(i)
				continue

			self.rotors[0].inverse_foward_pass(x)
			self.rotors[0].update_shift()
			
			z = alphabet[self.rotors[0].stored_value - 1]

			if not self.plugboard and use_plugboard:
				z = self.get_inverse_letter(alphabet[self.rotors[0].stored_value - 1])
				y.append(z)
			else:
				y.append(z)

		return ''.join(y)

class interface():
	def __init__(self):
		self.mac = machine()


	def run(self):
		while True:
			command = input('$ ')
			command = command.split()
			if command[0] == 'exit':
				exit()

			elif command[0] == 'add_rotor':
				if len(command) > 1:
					self.mac.add_rotor(int(command[1]))
					continue

				shift = input('shift = ')
				self.mac.add_rotor(int(shift))

			elif command[0] == 'set_plugboard':
				if len(command) > 1:
					self.mac.set_plugboard(command[1])
					continue

				plugboard = input('pl:')
				self.mac.set_plugboard(plugboard)

			elif command[0] == 'edit_rotors':
				rotors = []
				for x, y in zip(range(len(self.mac.rotors)), self.mac.rotors):
					rotors.append((x,y))
					print(f'Address: {x} == Shift: {y.shift_value}')

				
				index = input('Rotor Address = ')
				for i in rotors:
					if int(index) == i[0]:
						shift = int(input('new shift = ')) 
						self.mac.rotors[self.mac.rotors.index(i[1])].shift_value = shift

			elif command[0] == 'encrypt':
				text = input('e: ')
				if not self.mac.rotors:
					print('ERROR: NO ROTORS FOUND')
					continue

				print(self.mac.encrypt(text, use_plugboard=False))

			elif command[0] == 'decrypt':
				y = input('d: ')
				print(self.mac.decrypt(y, use_plugboard=False))

			elif command[0] == 'encrypt_file':
				filepath = None
				if len(command) > 1:
					filepath = command[1]
				else:	
					filepath = input('fp: ')
				file = open(filepath, 'r')
				encrypted_rows = []
				for row in file:
					encrypted_rows.append(self.mac.encrypt(row))
				new_file = open('encrypted.txt', 'w')
				for row in encrypted_rows:
					print(row)
					new_file.write(row)

			elif command[0] == 'decrypt_file':
				filepath = None
				if len(command) > 1:
					filepath = command[1]
				else:	
					filepath = input('fp: ')
				file = open(filepath, 'r')
				decrypted_rows = []
				for row in file:
					decrypted_rows.append(self.mac.decrypt(row))
				new_file = open('decrypted.txt', 'r')
				for row in decrypted_rows:
					new_file.write(row)

			else:
				print('Invalid Command')
				continue

inter = interface()
inter.run()