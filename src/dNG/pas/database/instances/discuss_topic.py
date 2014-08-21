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

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BIGINT, BOOLEAN, CHAR, VARCHAR

from dNG.pas.database.types.date_time import DateTime
from .data_linker import DataLinker
from .ownable_mixin import OwnableMixin

class DiscussTopic(DataLinker, OwnableMixin):
#
	"""
"DiscussTopic" represents a discussion topic.

:author:     direct Netware Group
:copyright:  direct Netware Group - All rights reserved
:package:    pas
:subpackage: discuss
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	__tablename__ = "{0}_discuss_topic".format(DataLinker.get_table_prefix())
	"""
SQLAlchemy table name
	"""
	db_instance_class = "dNG.pas.data.discuss.Topic"
	"""
Encapsulating SQLAlchemy database instance class name
	"""
	db_schema_version = 1
	"""
Database schema version
	"""

	id = Column(VARCHAR(32), ForeignKey(DataLinker.id), primary_key = True)
	"""
discuss_topic.id
	"""
	id_subscription = Column(VARCHAR(255), index = True)
	"""
discuss_topic.id_subscription
	"""
	owner_type = Column(CHAR(1), server_default = "u", nullable = False)
	"""
discuss_topic.owner_type
	"""
	author_id = Column(VARCHAR(32))
	"""
discuss_topic.author_id
	"""
	author_ip = Column(VARCHAR(100))
	"""
discuss_topic.author_ip
	"""
	posts = Column(BIGINT, server_default = "0", nullable = False)
	"""
discuss_topic.posts
	"""
	description = Column(VARCHAR(255), server_default = "", nullable = False)
	"""
discuss_topic.description
	"""
	time_published = Column(DateTime, index = True, nullable = False)
	"""
discuss_topic.time_published
	"""
	last_id_author = Column(VARCHAR(32))
	"""
discuss_topic.last_id_author
	"""
	last_preview = Column(VARCHAR(255))
	"""
discuss_topic.last_preview
	"""
	locked = Column(BOOLEAN, server_default = "0", nullable = False)
	"""
discuss_topic.locked
	"""
	guest_permission = Column(CHAR(1), server_default = "", nullable = False)
	"""
contentor_category.guest_permission
	"""
	user_permission = Column(CHAR(1), server_default = "", nullable = False)
	"""
contentor_category.user_permission
	"""

	__mapper_args__ = { "polymorphic_identity": "DiscussTopic" }
	"""
sqlalchemy.org: Other options are passed to mapper() using the
                __mapper_args__ class variable.
	"""

	def __init__(self, *args, **kwargs):
	#
		"""
Constructor __init__(DiscussTopic)

:since: v0.1.00
		"""

		DataLinker.__init__(self, *args, **kwargs)

		if (self.posts == None): self.posts = 0
	#
#

##j## EOF