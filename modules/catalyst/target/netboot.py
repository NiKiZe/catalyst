
"""
Builder class for a netboot build.
"""

import os,string,types
from catalyst.support import *
from generic_stage import *
import catalyst.util
from catalyst.error import *

class netboot_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.valid_values = [
			"netboot/kernel/sources",
			"netboot/kernel/config",
			"netboot/kernel/prebuilt",

			"netboot/busybox_config",

			"netboot/extra_files",
			"netboot/packages"
		]
		self.required_values=[]

		try:
			if "netboot/packages" in addlargs:
				if type(addlargs["netboot/packages"]) == types.StringType:
					loopy=[addlargs["netboot/packages"]]
				else:
					loopy=addlargs["netboot/packages"]

		#	for x in loopy:
		#		self.required_values.append("netboot/packages/"+x+"/files")
		except:
			raise CatalystError,"configuration error in netboot/packages."




		generic_stage_target.__init__(self,spec,addlargs)
		self.set_build_kernel_vars(addlargs)
		if "netboot/busybox_config" in addlargs:
			file_locate(self.settings, ["netboot/busybox_config"])

		# Custom Kernel Tarball --- use that instead ...

		# unless the user wants specific CFLAGS/CXXFLAGS, let's use -Os

		for envvar in "CFLAGS", "CXXFLAGS":
			if not envvar in os.environ and not envvar in addlargs:
				self.settings[envvar] = "-Os -pipe"


	def set_root_path(self):
		# ROOT= variable for emerges
		self.settings["root_path"]=catalyst.util.normpath("/tmp/image")
		print "netboot root path is "+self.settings["root_path"]

#	def build_packages(self):
#		# build packages
#		if "netboot/packages" in self.settings:
#			mypack = catalyst.util.list_bashify(self.settings["netboot/packages"])
#		try:
#			cmd("/bin/bash "+self.settings["controller_file"]+" packages "+mypack,env=self.env)
#		except CatalystError:
#			self.unbind()
#			raise CatalystError,"netboot build aborting due to error."

	def build_busybox(self):
		# build busybox
		if "netboot/busybox_config" in self.settings:
			mycmd = self.settings["netboot/busybox_config"]
		else:
			mycmd = ""
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+" busybox "+ mycmd,env=self.env)
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."


	def copy_files_to_image(self):
		# create image
		myfiles=[]
		if "netboot/packages" in self.settings:
			if type(self.settings["netboot/packages"]) == types.StringType:
				loopy=[self.settings["netboot/packages"]]
			else:
				loopy=self.settings["netboot/packages"]

		for x in loopy:
			if "netboot/packages/"+x+"/files" in self.settings:
			    if type(self.settings["netboot/packages/"+x+"/files"]) == types.ListType:
				    myfiles.extend(self.settings["netboot/packages/"+x+"/files"])
			    else:
				    myfiles.append(self.settings["netboot/packages/"+x+"/files"])

		if "netboot/extra_files" in self.settings:
			if type(self.settings["netboot/extra_files"]) == types.ListType:
				myfiles.extend(self.settings["netboot/extra_files"])
			else:
				myfiles.append(self.settings["netboot/extra_files"])

		try:
			cmd("/bin/bash "+self.settings["controller_file"]+\
				" image " + catalyst.util.list_bashify(myfiles),env=self.env)
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."


	def create_netboot_files(self):
		# finish it all up
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+" finish",env=self.env)
		except CatalystError:
			self.unbind()
			raise CatalystError,"netboot build aborting due to error."

		# end
		print "netboot: build finished !"


	def set_action_sequence(self):
	    self.settings["action_sequence"]=["unpack","unpack_snapshot",
	    				"config_profile_link","setup_confdir","bind","chroot_setup",\
						"setup_environment","build_packages","build_busybox",\
						"build_kernel","copy_files_to_image",\
						"clean","create_netboot_files","unbind","clear_autoresume"]

__target_map = {"netboot":netboot_target}
