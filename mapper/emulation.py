﻿# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import print_function

import codecs
import json
import os.path
import re
import threading

from .world import World
from .config import Config, config_lock
from .constants import DIRECTIONS, RUN_DESTINATION_REGEX, TERRAIN_SYMBOLS
from .utils import page, iterItems, getDirectoryPath

class EmulatedWorld(World):
	"""The main emulated world class"""
	def __init__(self, use_gui):

		self.output("Welcome to Mume Map Emulation!")
		self.output("Loading the world database.")
		World.__init__(self, use_gui=use_gui)
		self.output("Loaded {0} rooms.".format(len(self.rooms)))
		self.config = {}
		dataDirectory = getDirectoryPath("data")
		self.configFile = os.path.join(dataDirectory, "emulation_config.json")
		self.sampleConfigFile = os.path.join(dataDirectory, "emulation_config.json.sample")
		self.loadConfig()
		# Set the initial room to the room that the user was in when the program last terminated.
		lastVnum = self.config.get("last_vnum", "0")
		if lastVnum not in self.rooms:
			lastVnum = sorted(self.rooms)[0]
		self.move(lastVnum)

	def output(self, text):
		"""Output text with utils.page."""
		page(line for line in text.splitlines() if line.strip())

	def look(self):
		"""The 'look' command"""
		self.output(self.currentRoom.name)
		# If brief mode is disabled, output the room description
		if not self.config.get("brief", True):
			self.output(" ".join(line.strip() for line in self.currentRoom.desc.splitlines() if line.strip()))
		self.output(self.currentRoom.dynamicDesc)
		#loop through the list of exits in the current room, and build the doors/exits lines.
		doorList = []
		exitList = []
		for direction, exitObj in self.sortExits(self.currentRoom.exits):
			# If there is a door in that direction
			if exitObj.door or "door" in exitObj.exitFlags:
				doorList.append("{0}: {1}".format(direction, exitObj.door if exitObj.door else "exit"))
				if "hidden" not in exitObj.doorFlags:
					# The door is not a secret exit.
					# Enclose the direction of the door in parentheses '()' for use in the exits line. In Mume, enclosing an exits line direction in parentheses denotes an opened door in that direction.
					direction = "({0})".format(direction)
				else:
					# The door is a secret exit.
					# Enclose the direction of the door in brackets '[]' for use in the exits line. In Mume, enclosing an exits line direction in brackets denotes a closed door in that direction.
					direction = "[{0}]".format(direction)
			# The next 2 symbols which might be added are just convenience symbols for denoting if the exit is to an undefined room or a known deathtrap. They don't actually exist in Mume.
			if exitObj.to == "death":
				direction = "!!{0}!!".format(direction)
			elif exitObj.to not in self.rooms or exitObj.to == "undefined":
				direction = "??{0}??".format(direction)
			elif self.rooms[exitObj.to].terrain == "road":
				# The '=' sign is used in Mume to denote that the room in that direction is a road.
				direction = "={0}=".format(direction)
			elif "road" in exitObj.exitFlags:
				# The '-' sign is used in Mume to denote that the room in that direction is a trail.
				direction = "-{0}-".format(direction)
			exitList.append(direction)
		# If any of the exits had a door in that direction, print the direction and name of the door before the exits line.
		if doorList:
			self.output("Doors:")
			self.output(",\n".join(doorList))
		if not exitList:
			exitList.append("None!")
		self.output("Exits: {0}".format(", ".join(exitList)))
		if self.currentRoom.note:
			self.output("Note: {0}".format(self.currentRoom.note))
		# If the user has enabled the showing of room vnums in the configuration, print the room vnum.
		if self.config.get("show_vnum", True):
			self.output("Vnum: {0}".format(self.currentRoom.vnum))

	def longExits(self):
		"""The exits command"""
		self.output("Exits:")
		if not self.currentRoom.exits:
			return self.output("None!")
		for direction, exitObj in self.sortExits(self.currentRoom.exits):
			exitLine = []
			exitLine.append("{0}:".format(direction.capitalize()))
			if exitObj.door or "door" in exitObj.exitFlags:
				exitLine.append("{0} ({1}),".format("visible" if "hidden" not in exitObj.doorFlags else "hidden", exitObj.door if exitObj.door else "exit"))
			if exitObj.to.isdigit() and exitObj.to in self.rooms:
				exitLine.append("{0}, {1}".format(self.rooms[exitObj.to].name, self.rooms[exitObj.to].terrain))
			elif exitObj.to == "death":
				exitLine.append("death")
			else:
				exitLine.append("undefined")
			self.output(" ".join(exitLine))

	def move(self, text):
		"""Move to a given vnum, label, or in a given direction"""
		if text in DIRECTIONS:
			if text not in self.currentRoom.exits:
				return self.output("Alas, you cannot go that way!")
			else:
				vnum = self.currentRoom.exits[text].to
		elif text in self.labels:
			vnum = self.labels[text]
		elif text.isdigit():
			vnum = text
		else:
			return self.output("Error: {0} isn't a direction, label, or vnum.".format(text))
		if vnum == "undefined":
			return self.output("Undefined room in that direction!")
		elif vnum == "death":
			return self.output("Deathtrap in that direction!")
		elif vnum not in self.rooms:
			return self.output("Error: no rooms in the database with vnum ({0}).".format(vnum))
		self.currentRoom = self.rooms[vnum]
		self.config["last_vnum"] = vnum
		self.look()

	def toggleSetting(self, setting):
		"""Toggle configuration settings True/False"""
		self.config[setting] = self.config.get(setting, True) == False
		return self.config[setting]

	def loadConfig(self):
		"""Load the configuration file"""
		def getConfig(fileName):
			if os.path.exists(fileName):
				if not os.path.isdir(fileName):
					try:
						with codecs.open(fileName, "rb", encoding="utf-8") as fileObj:
							return json.load(fileObj)
					except IOError as e:
						self.output("{0}: '{1}'".format(e.strerror, e.filename))
						return {}
					except ValueError as e:
						self.output("Corrupted configuration file: {0}".format(fileName))
						return {}
				else:
					self.output("Error: '{0}' is a directory, not a file.".format(fileName))
					return {}
			else:
				return {}
		self.config.update(getConfig(self.sampleConfigFile))
		self.config.update(getConfig(self.configFile))

	def saveConfig(self):
		"""Save the configuration to disk"""
		with codecs.open(self.configFile, "wb", "utf-8") as fileObj:
			json.dump(self.config, fileObj, sort_keys=True, indent=2, separators=(",", ": "))

	def parseInput(self, userInput):
		"""Parse the user input"""
		match = re.match(r"^(?P<command>\S+)(?:\s+(?P<arguments>.*))?", userInput)
		command = match.group("command")
		arguments = match.group("arguments")
		direction = "".join(dir for dir in DIRECTIONS if dir.startswith(command))
		if direction:
			self.move(direction)
		elif "look".startswith(command):
			self.look()
		elif "exits".startswith(command):
			self.longExits()
		elif command == "vnum":
			status = self.toggleSetting("show_vnum")
			self.output("Show room vnum {0}.".format("enabled" if status else "disabled"))
		elif command == "brief":
			status = self.toggleSetting("brief")
			self.output("Brief mode {0}.".format("enabled" if status else "disabled"))
		elif command == "terrain":
			status = self.toggleSetting("use_terrain_symbols")
			self.output("Terrain symbols in prompt {0}.".format("enabled" if status else "disabled"))
		elif command == "path":
			if not arguments:
				self.pathFind()
			else:
				match = RUN_DESTINATION_REGEX.match(arguments)
				destination = match.group("destination")
				flags = match.group("flags")
				if flags:
					flags = flags.split("|")
				else:
					flags = None
				result = self.pathFind(destination=destination, flags=flags)
				if result is not None:
					self.output(self.createSpeedWalk(result))
		elif command == "rlabel":
			result = self.rlabel(arguments)
			if result:
				self.output("\n".join(result))
		elif command == "rinfo":
			self.output("\n".join(self.rinfo(arguments)))
		elif command in ("fdoor", "fname", "fnote", "rnote", "ralign", "rlight", "rportable", "rridable", "ravoid", "rterrain", "rx", "ry", "rz", "rmobflags", "rloadflags", "exitflags", "doorflags", "secret", "rlink", "rdelete"):
			self.output(getattr(self, command)(arguments))
		elif command == "savemap":
			self.saveRooms()
		elif command.isdigit() or command in self.labels:
			self.move(command)
		else:
			self.output("Arglebargle, glop-glyf!?!")


class Emulator(threading.Thread):
	def __init__(self, use_gui):
		threading.Thread.__init__(self)
		self.name = "Emulator"
		self.world = EmulatedWorld(use_gui)
		self._use_gui = use_gui

	def run(self):
		wld = self.world
		while True:
			prompt = "> "
			# Indicate the current room's terrain in the prompt.
			if not wld.config.get("use_terrain_symbols"):
				prompt = wld.currentRoom.terrain + prompt
			else:
				for symbol, terrain in iterItems(TERRAIN_SYMBOLS):
					if terrain == wld.currentRoom.terrain:
						prompt = symbol + prompt
						break
			# For Python 2/3 compatibility:
			try:
				userInput = raw_input(prompt).strip().lower()
			except NameError:
				userInput = input(prompt).strip().lower()
			if not userInput:
				continue
			elif "quit".startswith(userInput):
				break
			else:
				wld.parseInput(userInput)
		# The user has typed 'q[uit]'. Save the config file and exit.
		wld.saveConfig()
		wld.output("Good bye.")
		if self._use_gui:
			with wld._gui_queue_lock:
				wld._gui_queue.put(None)


def main(use_gui=True):
	if use_gui is True:
		# The user wants to use a GUI, but didn't specify which one. Grab the preferred GUI option from the configuration.
		from . import use_gui
	if use_gui :
		use_gui = use_gui.strip().lower()
		try:
			import pyglet
		except ImportError:
			print("Unable to find pyglet. Disabling gui")
			use_gui = False
	emulator_thread=Emulator(use_gui)
	emulator_thread.start()
	if use_gui:
		pyglet.app.run()
	emulator_thread.join()
