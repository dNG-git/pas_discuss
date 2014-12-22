# -*- coding: utf-8 -*-
##j## BOF

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;discuss

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasDiscussVersion)#
#echo(__FILEPATH__)#
"""

from time import time

from dNG.pas.data.binary import Binary
from dNG.pas.data.data_linker import DataLinker
from dNG.pas.data.ownable_lockable_read_mixin import OwnableLockableReadMixin
from dNG.pas.database.lockable_mixin import LockableMixin
from dNG.pas.database.instances.discuss_post import DiscussPost as _DbDiscussPost
from dNG.pas.database.instances.text_entry import TextEntry as _DbTextEntry
from .list import List
from .topic import Topic

class Post(DataLinker, LockableMixin, OwnableLockableReadMixin):
#
	"""
"Post" represents a single discussion post.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: discuss
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self, db_instance = None):
	#
		"""
Constructor __init__(Post)

:param db_instance: Encapsulated SQLAlchemy database instance

:since: v0.1.00
		"""

		DataLinker.__init__(self, db_instance)
		LockableMixin.__init__(self)
		OwnableLockableReadMixin.__init__(self)
	#

	def add_reply_post(self, post):
	#
		"""
Add the given child post.

:param post: DiscussPost instance
:param post_preview: Post preview

:since: v0.1.00
		"""

		# pylint: disable=protected-access

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.add_reply_post()- (#echo(__LINE__)#)", self, context = "pas_datalinker")

		if (isinstance(post, Post)):
		#
			with self:
			#
				if (post.get_id() != self.local.db_instance.id):
				#
					self.local.db_instance.rel_children.append(post._get_db_instance())
				#
			#
		#
	#

	def delete(self):
	#
		"""
Deletes this entry from the database.

:since: v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.delete()- (#echo(__LINE__)#)", self, context = "pas_datalinker")

		with self:
		#
			db_text_entry_instance = self.local.db_instance.rel_text_entry

			DataLinker.delete(self)
			if (db_text_entry_instance is not None): self.local.connection.delete(db_text_entry_instance)
		#
	#

	def get_sub_entries(self, offset = 0, limit = -1):
	#
		"""
Returns the child entries of this instance.

:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) DataLinker children instances
:since:  v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_sub_entries({1:d}, {2:d})- (#echo(__LINE__)#)", self, offset, limit, context = "pas_datalinker")
		return DataLinker.get_sub_entries(self, offset, limit, exclude_identity = "DiscussPost")
	#

	def get_sub_entries_count(self):
	#
		"""
Returns the number of child entries of this instance.

:return: (int) Number of child entries
:since:  v0.1.00
		"""

		return DataLinker.get_sub_entries_count(self, exclude_identity = "DiscussPost")
	#

	def get_reply_posts(self, offset = 0, limit = -1):
	#
		"""
Returns the children reply posts of this instance.

:param offset: SQLAlchemy query offset
:param limit: SQLAlchemy query limit

:return: (list) Post children instances
:since:  v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}.get_reply_posts({1:d}, {2:d})- (#echo(__LINE__)#)", self, offset, limit, context = "pas_datalinker")
		return DataLinker.get_sub_entries(self, offset, limit, identity = "DiscussPost")
	#

	def get_reply_posts_count(self):
	#
		"""
Returns the number of reply posts of this instance.

:return: (int) Number of child posts
:since:  v0.1.00
		"""

		return DataLinker.get_sub_entries_count(self, identity = "DiscussPost")
	#

	def _get_unknown_data_attribute(self, attribute):
	#
		"""
Returns the data for the requested attribute not defined for this instance.

:param attribute: Requested attribute

:return: (dict) Value for the requested attribute
:since:  v0.1.00
		"""

		if (attribute == "content" and self.local.db_instance.rel_text_entry is not None): _return = self.local.db_instance.rel_text_entry.content
		else: _return = DataLinker._get_unknown_data_attribute(self, attribute)

		return _return
	#

	def _insert(self):
	#
		"""
Insert the instance into the database.

:since: v0.1.00
		"""

		DataLinker._insert(self)

		with self.local.connection.no_autoflush:
		#
			if (self.local.db_instance.time_published is None): self.local.db_instance.time_published = int(time())

			data_missing = (self.is_data_attribute_none("owner_type", "posts", "guest_permission", "user_permission"))
			acl_missing = (len(self.local.db_instance.rel_acl) == 0)
			parent_object = (self.load_main() if (data_missing or acl_missing) else None)
			is_parent_topic = isinstance(parent_object, Topic)

			if (data_missing and (is_parent_topic or isinstance(parent_object, List))):
			#
				parent_data = parent_object.get_data_attributes("id_site", "owner_type", "guest_permission", "user_permission")

				if (self.local.db_instance.id_site is None and parent_data['id_site'] is not None): self.local.db_instance.id_site = parent_data['id_site']
				if (self.local.db_instance.owner_type is None): self.local.db_instance.owner_type = parent_data['owner_type']
				if (is_parent_topic): self.local.db_instance.position = parent_object._get_db_instance().posts
				if (self.local.db_instance.guest_permission is None): self.local.db_instance.guest_permission = parent_data['guest_permission']
				if (self.local.db_instance.user_permission is None): self.local.db_instance.user_permission = parent_data['user_permission']
			#

			# TODO: if (acl_missing and isinstance(parent_object, OwnableLockableReadMixin)): self.data.acl_set_list(parent_object.data_acl_get_list())
		#
	#

	def set_data_attributes(self, **kwargs):
	#
		"""
Sets values given as keyword arguments to this method.

:since: v0.1.00
		"""

		self._ensure_thread_local_instance(_DbDiscussPost)

		with self, self.local.connection.no_autoflush:
		#
			DataLinker.set_data_attributes(self, **kwargs)

			if ("owner_type" in kwargs): self.local.db_instance.owner_type = kwargs['owner_type']
			if ("author_id" in kwargs): self.local.db_instance.author_id = kwargs['author_id']
			if ("author_ip" in kwargs): self.local.db_instance.author_ip = kwargs['author_ip']
			if ("time_published" in kwargs): self.local.db_instance.time_published = int(kwargs['time_published'])
			if ("preserve_space" in kwargs): self.local.db_instance.preserve_space = kwargs['preserve_space']
			if ("locked" in kwargs): self.local.db_instance.locked = kwargs['locked']
			if ("guest_permission" in kwargs): self.local.db_instance.guest_permission = kwargs['guest_permission']
			if ("user_permission" in kwargs): self.local.db_instance.user_permission = kwargs['user_permission']

			if ("content" in kwargs):
			#
				if (self.local.db_instance.rel_text_entry is None):
				#
					self.local.db_instance.rel_text_entry = _DbTextEntry()
					self.local.db_instance.rel_text_entry.id = self.local.db_instance.id
					db_text_entry = self.local.db_instance.rel_text_entry
				#
				else: db_text_entry = self.local.db_instance.rel_text_entry

				db_text_entry.content = Binary.utf8(kwargs['content'])
			#
		#
	#

	def _set_id(self, _id):
	#
		"""
Sets the post ID.

:param _id: Post ID

:since: v0.1.00
		"""

		if (self.log_handler is not None): self.log_handler.debug("#echo(__FILEPATH__)# -{0!r}._set_id({1})- (#echo(__LINE__)#)", self, _id, context = "pas_datalinker")

		self._ensure_thread_local_instance(_DbDiscussPost)
		with self: self.local.db_instance.id = _id
	#
#

##j## EOF