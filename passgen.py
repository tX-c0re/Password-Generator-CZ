import psutil
import sys
import time
import click
from perm_classes import *
from utils import *


class main_ganerator:
	def __init__(self, level=0, pwd_min=8, pwd_max=12, num_range=0,
				 leeter=False, years=0, chars=True, verbose=True, export='hesla.txt'):
		# Úrovně komplikací:
        # 0 = výchozí
        # 1 = 0 + umožňuje více permutací v perm_classes
        # 2 = 1 + umožňuje více permutací ve třídě perm starých hesel
        # 3 = 2 + Použití celé sady speciálních znaků povolených v heslech
        # 4 = 3 + Použijte více permutací v hlavní funkci
        # 5 = 4 + Nepoužívejte objednané páry pro funkci trvalé
        # pokud chcete více, povolte leeter, je to úroveň 666 lol!
		self.shit_level   = level
		self.verbose_mode = verbose
		# Okay lesgooo!
		self.names = names_perm
		self.dates = dates_perm
		self.phones = phones_perm
		self.old_passwords = oldpwds
		self.total_result = []
		# Proměnné délky hesel
		self.minimum_length = pwd_min
		self.maximum_length = pwd_max
		# Úroveň hloubky 
		# Pro banner a kontrolu
		self.number_range = f"{B}{num_range}{reset + W}" if num_range != 0 else f"{R}Nepravda{reset + W}"
		self.years_range = f"{B}{years}-{time.localtime().tm_year + 1}{reset + W}" if years != 0 else f"{R}Nepravda{reset + W}"
		if chars:
			self.special_chars = f"{B}Všechny znaky{reset + W}" if self.shit_level >= 3 else f"{B}Běžné znaky{reset + W}"
		else:
			self.special_chars = f"{R}Zakázáno{reset + W}"
		self.leeting = f"{B}Povoleno{reset + W}" if leeter else f"{R}Zakázáno{reset + W}"
		# For looping
		self.recipes = [[]]
		if num_range != 0:
			self.recipes.append(data_plus.nums_range(num_range))
		if years != 0:
			self.recipes.append(data_plus.years(years))
		if chars:
			if self.shit_level >= 3:
				self.recipes.append(data_plus.chars)
			else:
				self.recipes.append(("_", ".", "-", "!", "@", "*", "$", "?", "&",
									 "%"))  # Běžné speciální znaky podle tohoto vlákna (https://www.reddit.com/r/dataisbeautiful/comments/2vfgvh/most_frequentlyused_special_characters_in_10/)
		self.add_leet_perms = leeter
		self.export_file = export

	def __input(self, prompt):
		result = []
		while True:
			# Workaround Řešení, protože colorama z nějakého důvodu netiskne barevné texty pomocí input() !!
			print(f"{G}[{reset + B}>{reset + G}] {prompt}{reset}", end="")
			data = input()
			print(f"{reset}", end="")
			if data:
				if " " in data.strip():
					data = data.split(" ")
				else:
					data = [data]
				for part in data:
					for smaller_part in part.split(","):
						if smaller_part:
							result.append(smaller_part)
			return result

	def __pwd_check(self, pwd):
		if (len(pwd) >= self.minimum_length) and (len(pwd) <= self.maximum_length) and (pwd not in self.total_result):
			return True
		return False

	def __simple_perm(self, target, *groups):
		for pair in zip(*groups, fillvalue=""):
			for targeted in target:
				pair = (targeted,) + pair
				for addition in self.recipes:
					yield ("".join(pair + (added,)) for added in addition)

	def __commonPerms(self):
		# Jen abychom se ujistili, že běžné perm jsou v permutacích
		for name in self.names.words:
			if self.__pwd_check(name):
				self.total_result.append(name)
		for date in self.dates.joined_dates:
			if self.__pwd_check(date):
				self.total_result.append(date)
			for thing in [self.names.words, self.names.one, self.names.two]:
				for justone in thing:
					if self.__pwd_check(justone + date):
						self.total_result.append(justone + date)
		for national_number in self.phones.national:
			if self.__pwd_check(national_number):
				self.total_result.append(national_number)
			for thing in [self.names.words, self.names.one, self.names.two]:
				for justone in thing:
					if self.__pwd_check(justone + national_number):
						self.total_result.append(justone + national_number)

	def __perm(self, target, *groups, perm_length=None):
		# Vratí všechny permutace kombinovaných iterátorů/generátorů
		if groups:
			perm_length = perm_length if perm_length else len(groups) + 1
			if self.shit_level >= 5:
				# Chceš vidět více výsledků?,
				#      tak nepřeskakuj permutace,
				#          pokud nechceš vidět nerealistické permutace
				#              Poté si přišel na správné místo  :laughing:
				for pair in ((target, pair2) for pair2 in groups):
					for addition in self.recipes:
						iterator = chain.from_iterable(pair + (addition,))
						yield ("".join(p) for p in perm(iterator, perm_length) if
							   (self.__pwd_check("".join(p)) and not ("".join(p)).isdecimal()))
			else:
				# Pokud chcete, aby to nebylo složité pro realističtější výsledky, použijte takto uspořádané dvojice
				# Možná, že se mýlím? PR s tím, co považujete za nejlepší realistický výsledek bez chaosu :)
				for targeted in target:
					for pair in (((targeted,) + pairs) for pairs in zip(*groups, fillvalue="")):
						for addition in self.recipes:
							if not addition:
								yield ("".join(p) for p in perm(pair, perm_length) if
									   (self.__pwd_check("".join(p)) and not ("".join(p)).isdecimal()))
							else:
								for added in addition:
									# iterator = chain.from_iterable(pair+(added,))
									iterator = pair + (added,)
									yield ("".join(p) for p in perm(iterator, perm_length) if
										   (self.__pwd_check("".join(p)) and not ("".join(p)).isdecimal()))

	def __perms(self, *main_group, others, perm_length=None):
		# Vrátí kombinované permutace (main_group, other_group)
		# Toto je napsáno, aby byl kód čistší místo toho, abyste nemuseli mnohokrát psat self.perm
		iters = []
		for other_group in others:
			iters.append(self.__perm(*main_group, other_group, perm_length=perm_length))
		iters.append(self.__perm(*main_group, *others, perm_length=perm_length))
		return chain.from_iterable(iters)

	def __export(self):
		# Řádek po řádku je pomalejší, ale efektivní z hlediska paměti (velmi velké výsledky by se nevešly do paměti RAM)
		if self.total_result:
			sys.stdout.write(f"[~] Exportuji výsledky do {self.export_file}...\r")
			sys.stdout.flush()
			with open(self.export_file, 'w') as f:
				for pwd in self.total_result:
					f.write(f"{pwd}\n")
			print(f"[+] Výsledky exportováný do {self.export_file}!")

	def perms_generator(self):
		# Běžná hesla před spuštěním permutací
		self.__commonPerms()
		# Začneme s permutací
		mixes = [
			# Jenom jména
			self.__simple_perm(self.names.words, ),
			# Jména a datumy
			self.__perms(self.names.words, others=(self.dates.days, self.dates.months, self.dates.years), ),
			# Jména a mobilní čísla
			self.__perm(self.names.one, self.dates.joined_dates, ),
			self.__perm(self.names.two, self.dates.joined_dates, ),
			self.__perms(self.names.words,
						 others=(self.phones.national, self.phones.first_four, self.phones.last_four), ),
			self.__perm(self.names.one, self.phones.national, ),
			self.__perm(self.names.two, self.phones.national, ),
			self.__perms(self.names.one, others=(self.phones.first_four, self.phones.last_four), ),
			self.__perms(self.names.two, others=(self.phones.first_four, self.phones.last_four), ),
			# Jména, datumy, mobilní čísla
			self.__perm(self.names.words, self.dates.years, self.phones.first_four, ),
			self.__perm(self.names.words, self.dates.years, self.phones.last_four, ),
			self.__perm(self.names.words, self.dates.years, self.phones.national, )]
		# V tuto chvíli přidáme stará hesla
		if self.old_passwords.passwords:
			for pwd in self.old_passwords.passwords:
				# Zde nezískáme všechny permutace, protože lidé mají tendenci pouze přidávat nové věci ke starým heslům, aniž by je hodně měnili!
				for iterator in (data_plus.nums_range(100), data_plus.years(1900), data_plus.chars,):
					mixes.append(
						("".join(p) for one in iterator for p in perm((pwd, one), 2) if self.__pwd_check("".join(p))))
			mixes.append(self.__perm(self.old_passwords.passwords, self.names.words, ))
			mixes.append(self.__perms(self.old_passwords.passwords,
									  others=(self.dates.days, self.dates.months, self.dates.years), ))
			mixes.append(self.__perms(self.old_passwords.passwords,
									  others=(self.phones.national, self.phones.first_four, self.phones.last_four), ))
		#######################################################################
		# Složitější nepříliš běžné ani realistické
		if self.shit_level >= 4:
			# jména, datumy
			mixes.append(self.__perm(self.names.words, self.dates.days, self.dates.months, self.dates.years))
			mixes.append(self.__perm(self.names.one, self.names.two, self.dates.joined_dates))
			# jména, telefony
			mixes.append(self.__perm(self.names.words, self.phones.first_four, self.phones.last_four))
			mixes.append(self.__perm(self.names.one, self.names.two, self.phones.national))
			mixes.append(self.__perm(self.names.one, self.names.two, self.phones.first_four, self.phones.last_four, ))
			# jména, datumy, telefony
			mixes.append(
				self.__perm(self.names.words, self.dates.years, self.phones.first_four, self.phones.last_four, ))
			mixes.append(self.__perm(self.names.words, self.dates.days, self.dates.months, self.phones.national, ))
			# telefony, datumy...atd čísla jsou v jiných variacích
			mixes.append(self.__perm(self.dates.days, self.dates.months, self.dates.years, ))
			mixes.append(self.__perm(self.phones.national, self.dates.years, ))
			mixes.append(self.__perm(self.phones.first_four, self.phones.last_four, self.dates.years, ))
		######################
		sys.stdout.write("[~] Generuji hesla...\r")
		sys.stdout.flush()
		for generator in chain.from_iterable(mixes):
			for pwd in generator:
				if self.__pwd_check(pwd):
					# print(pwd, flush=True)
					self.total_result.append(pwd)
					if self.verbose_mode:
						sys.stdout.write(f"[~] Generuji hesla: {pwd : <25} [N:{len(self.total_result) :_<10}]\r")
						sys.stdout.flush()

		print(f"[+] Celkový počet: {str(len(self.total_result))+' hesel': <40}")
		self.__export()
		if self.add_leet_perms:
			print("[~] Nyní vytvářím nový soubor s permutacemi pro každé vygenerované heslo...")
			del self.total_result[:]
			self.total_result = []
			with open(self.export_file, 'r') as data:
				for pwd in data:
					self.total_result.extend(data_plus.leet_perm(pwd.strip()))
			self.export_file = "Leeted-"+self.export_file
			print(f"[+] Celkový počet leeted hesel: {len(self.total_result)} hesel")
			self.__export()

	def __print_banner(self):
		with open("banner.txt") as f:
			banner_text = f.read()
			print(W + banner_text.format(
				ver=f"{reset}{B}2.0{reset}{W}",
				num=self.number_range, year=self.years_range,
				chars=self.special_chars,
				leet=self.leeting,
				min=f"{reset}{B}{self.minimum_length}{reset}{G}", max=f"{reset}{B}{self.maximum_length}{reset}{G}",
				verbose={
					True: f"{B}Povoleno{reset + W}",
					False: f"{R}Zakázáno{reset + W}"
				}[self.verbose_mode], export=f"{B}{self.export_file}{reset + W}",
				# 0 = výchozí
                # 1 = 0 + umožňuje více permutací v perm_classes
                # 2 = 1 + umožňuje více permutací ve třídě perm starých hesel
                # 3 = 2 + Použití celé sady speciálních znaků povolených v heslech
                # 4 = 3 + Nepoužívejte objednané páry pro funkci trvalé
                # 5 = 4 + Použijte více permutací v hlavní funkci
				level=reset+C+{
					0: "Prostý člověk",
					1: "Průměrný člověk",
					2: "Kybernetické povědomí",
					3: "Paranoidní osoba",
					4: "Nerd osoba",
					5: "Jaderná",
				}[self.shit_level]+reset+G,
				G=G, end=reset + W
			) + reset)

	def interface(self):
		self.__print_banner()
		self.names = self.names(self.__input("Jméno (Bez mezer, pokud se jedná o více jmen odděl - (Jméno Jméno)): "),
								complicated=self.shit_level)
		self.names.add_keywords(     
			self.__input("Jákékoliv klíčové slova přezdívka, práce, filmy, seriály... Bez mezer, odděl - (Přezdívka Prace): "))
		self.dates = self.dates(
			self.__input("Datum narození (Formát: [dd-mm-yyyy] ): "),
			complicated=self.shit_level)
		self.phones = self.phones(
			self.__input("Tel. číslo (Format: [+Předvolba státu...] např: +420123456999 odděl - (Tel.číslo Tel.číslo)): "))
		self.old_passwords = self.old_passwords(
			self.__input("Staré heslo, pokud neznáš, zkus použít slova, která by mohla představovat nové heslo (odděl Heslo Heslo): "),
			complicated=self.shit_level)
		start_time = time.time()
		try:
			self.perms_generator()
		except KeyboardInterrupt:
			print('[!] Přerušeno pomocí příkazu (Ctrl+C)! Ukončuji...')
			self.__export()
		finally:
			process = psutil.Process(os.getpid())
			elapsed = round(time.time()-start_time, 2)
			if elapsed >= 60:
				elapsed /= 60
				elapsed = str(round(elapsed, 2))+"m"
			else:
				elapsed = str(elapsed)+"s"
			# usage in megabytes
			print(f"[+] Uplynulý čas {elapsed} - Využití paměti (rss:{round(process.memory_info().rss / 1024 ** 2, 2)}MB vms:{round(process.memory_info().vms / 1024 ** 2, 2)}MB)")
			sys.exit(0)


@click.command()
@click.option('-l', '--level', metavar='', type=click.Choice(['0', '1', '2', '3', '4', '5']), default='0', help='Level komplikovanosti hesla.')
@click.option('--min', 'pmin', metavar='', type=int, default=8, help='Minimální délka hesla (Výchozí:8).')
@click.option('--max', 'pmax', metavar='', type=int, default=12, help='Maximální délka hesla (Výchozí:12).')
@click.option('-r', '--num-range', metavar='', type=int, default=0, help='Rozsah čísel, které se mají přidat do mixu (začněte od 0 do vámi určeného).')
@click.option('--leet', metavar='', is_flag=True, default=False, help='Získá všechny Leetovy permutace hesel po dokončení v jiném souboru.')
@click.option('-y', '--years', metavar='', type=int, default=0, help='Přidá do mixu všechny roky od daného do dalšího roku, ve kterém se nacházíme.')
@click.option('-c', '--chars', metavar='', is_flag=True, default=False, help='Přidá do mixu běžné speciální znaky, ale na úrovni 3 a vyšší používá celou sadu speciálních znaků povolenou v heslech.')
@click.option('-v', '--verbose', metavar='', is_flag=True, default=False, help='Aktivuje podrobný režim, takže všechna hesla se vám vytisknou během generování (dokončení RBPASS CRACK bude trvat dvakrát déle).')
@click.option('-x', '--export', metavar='', type=str, default='Hesla.txt', help='Název souboru, do kterého chcete exportovat výsledky.')
def main(level, pmin, pmax, num_range, leet, years, chars, verbose, export):
	gen = main_ganerator(int(level), pmin, pmax, num_range, leet, years, chars, verbose, export)
	gen.interface()


if __name__ == '__main__':
	main()
