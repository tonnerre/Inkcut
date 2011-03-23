#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       File: job.py
#       Date: 11 March 2011
#
#       Copyright 2011 Jairus Martin <jrm5555@psu.edu>
#
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
from datetime import datetime
from unit import unit
from lxml import etree


# Database model
from sqlalchemy import Table, Column, Integer, Float, UnicodeText,DateTime, Unicode, ForeignKey, Boolean
from meta import Base

class Job(Base):
    """
    Job specificiations, properties, and requirements for converting
    from a graphic to the output format.  Interacts with a database
    to keep track of jobs.
    """
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    description = Column(UnicodeText)
    created = Column(DateTime,default=datetime.now())
    source_filename = Column(Unicode,unique=True)
    source_last_modified = Column(DateTime)
    source = Column(UnicodeText,nullable=False)
    data = Column(UnicodeText)
    status = Column(Unicode)
    device_id = Column(Integer, ForeignKey('devices.id'))
    material_id = Column(Integer, ForeignKey('materials.id'))
    requirements_id = Column(Integer, ForeignKey('job_requirements.id'))

    def __init__(self):
        """
        Create a job instance with it's undefined properties.
        """
        self.id = None
        self.name = None
        self.description = None
        self.created = datetime.now()
        self.source_filename = None # original graphic source filename
        self.source_last_modified = None
        self.source = None # original graphic source file
        self.data = None # inkcut created and modified svg
        self.status = None
        self.device = None
        self.material = None

        # Job requirements
        self.requirements = JobRequirements()

        # Job status flags
        self.status = 'Unprocessed'
        self.messages = []

    # Job managment
    def create(self,
            id=None,
            name=None,
            description=None,
            created=datetime.now(),
            source_filename=None,
            source_last_modified=None,
            source=None,
            data=None,
            status=u'New Job: Unprocessed',
            device=None,
            material=None,
            **kwargs
            ):
        """ Creates a database entry and loads a source graphic """
        self.id = id
        self.name = name
        self.description = description
        self.created = created
        self.source_filename = source_filename
        self.source_last_modified = source_last_modified
        self.source = source # svg etree._ElementTree
        self.data = data # modified svg file
        self.status = status
        self.device = device
        self.material = material

        # Job requirements
        self.requirements = JobRequirements(kwargs)

        self.process()
        return self

    def load(self,source=None,source_filename=None,selected_nodes=None):
        """ tries to find a database entry if not creates a new one """
        # if in_database:
        #   return self.read(id)
        # else:
        #   return self.create():
        if type(source) == etree._ElementTree:
            self.create(source=source,
                    source_filename=source_filename,
                    selected_nodes=selected_nodes)
            return True
        elif source_filename is not None:
            try:
                source = etree.parse(source_filename)
                self.create(source=source,
                    source_filename=source_filename,
                    selected_nodes=selected_nodes)
                return True
            except (IOError,etree.XMLSyntaxError):
                self.messages.append('Could not open the file: %s. \n Reason: Invalid filetype or file not found.'% source_filename)
                return False

        self.messages.append('Could not open the source file.')
        return False



    def read(self,id):
        """ Loads a job from the database """
        pass

    def delete():
        """ Removes a job from the database, logs the activity """
        pass

    # Job requirements
    def requirements(self):
        """ Returns a dictionary of the job requirements """
        return self.properties

    def requirement(self,key,value=None):
        """
        Reads the requirement with given key.  If a value is passed it
        sets the requirment to that value.
        """
        pass

    # Job processing
    def process(self):
        """
        Converts the source svg to data svg using job requirements.
        """
        self.data = self.source

    def validate(self):
        """
        Checks that the job can be done given the material and device.
        Returns boolean, appends any errors and dispatches messages
        """
        pass

    def submit(self):
        """
        Submits a job to be handled by the job device. Returns a status.
        """
        self.process()
        if self.validate():
            self.status = 'Sending to device...'
            self.device.submit(self.data)

        pass

    # Job properties
    def properties(self):
        """ Returns a dictionary of the job properties """
        return {'height': None, 'width': None,  'length': 0}

    def status(self):
        """ Returns job status """
        return self.status

class JobRequirements(Base):
    """
    Job requirements, so it can be easily changed it's separated from
    the job
    """
    __tablename__ = 'job_requirements'
    id = Column(Integer, primary_key=True)
    copies = Column(Integer)
    scale_x = Column(Float)
    scale_y = Column(Float)
    scale_lock = Column(Boolean)
    start_x = Column(Integer)
    start_y = Column(Integer)
    center_x = Column(Boolean)
    center_y = Column(Boolean)
    invert_axis_x = Column(Boolean)
    invert_axis_y = Column(Boolean)
    plot_margin_top = Column(Float)
    plot_margin_right = Column(Float)
    plot_margin_bottom = Column(Float)
    plot_margin_left = Column(Float)
    copy_spacing_x = Column(Float)
    copy_spacing_y = Column(Float)
    copy_rotation = Column(Float)
    path_smoothness = Column(Float)
    path_sort_order = Column(Integer)
    weed_plot = Column(Boolean)
    weed_plot_margin = Column(Float)
    weed_copy = Column(Boolean)
    weed_copy_margin = Column(Float)
    plot_selected_nodes = Column(UnicodeText)

    def __init__(self,
            id=None,
            copies=1,
            scale_x=1,
            scale_y=1,
            scale_lock=1,
            start_x=0,
            start_y=0,
            center_x=False,
            center_y=False,
            invert_axis_x=True,
            invert_axis_y=False,
            plot_margin_top=0,
            plot_margin_right=0,
            plot_margin_bottom=0,
            plot_margin_left=0,
            copy_spacing_x=unit(.25,'cm'), # TODO: load from config
            copy_spacing_y=unit(.25,'cm'), # TODO: load from config
            copy_rotation=0,
            path_smoothness=0.2,
            path_sort_order=0,
            weed_plot=False,
            weed_plot_margin=0,
            weed_copy=False,
            weed_copy_margin=0,
            plot_selected_nodes=None
        ):
        # Job requirements
        self.copies = copies
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.scale_lock = scale_lock
        self.start_x = start_x
        self.start_y = start_y
        self.center_x = center_x
        self.center_y = center_y
        self.invert_axis_x = invert_axis_x
        self.invert_axis_y = invert_axis_y
        self.plot_margin_top = plot_margin_top
        self.plot_margin_right = plot_margin_right
        self.plot_margin_bottom = plot_margin_bottom
        self.plot_margin_left = plot_margin_left
        self.copy_spacing_x = copy_spacing_x
        self.copy_spacing_y = copy_spacing_y
        self.copy_rotation = copy_rotation
        self.path_smoothness = path_smoothness
        self.path_sort_order = path_sort_order
        self.weed_plot = weed_plot
        self.weed_plot_margin = weed_plot_margin
        self.weed_copy = weed_copy
        self.weed_copy_margin = weed_copy_margin
        self.plot_selected_nodes = plot_selected_nodes

        # Job status flags
        self.changed = True