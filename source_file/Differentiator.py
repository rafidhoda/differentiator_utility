# made by Rafid Hoda for PetroStreamz
import linecache
import os
from sympy import sin, cos, Function, diff
from sympy.abc import x, y
from sympy.core import Symbol
from sys import argv
import sys
# for xml reader
import re
import xml.sax.handler
from xml.dom.minidom import Document


# this flushes all print statements
sys.stdout.flush()

splash = """
*************************************************
*                                               *
*                Differentiator                 *
*                                               *
*               Version 20120302                *
*                                               *
*      (c) Copyright Petrostreamz 2012          *
*              All Rights Reserved              *
*                                               *
*************************************************
""" 

print splash

# if no in put or output selected
try:
   script, inPath, outPath, userType = argv
except:
   sys.exit("ERROR: No input or/and output file or/and differentiation type.")

script, inPath, outPath, userType = argv
   
# userTypes
ppo2ppo = "ppo2ppo"
txt2ppo = "txt2ppo"
txt2txt = "txt2txt"

input_file = open(inPath, 'r').read()


#Global messages
m_variable_defined = "Defined %s as variable."
m_diff_with_respect_to = "Differentiated %s with respect to %s."
m_diff_complete = """
Differentiation Completed."""
m_error_userType = "ERROR: Please choose txt2txt, txt2ppo or ppo2ppo as differentiation type."
m_invalid_input = "ERROR: Invalid input file."
check_if_xml = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"

optimization_end_tag = "</Optimization>"

#Global variables
exponent_python = "**"
exponent_pipeit = "^"
colon = ":"
var_list = []

# check to see if input file is valid:
first_line_input = str(linecache.getline(inPath, 1))

if ( userType == txt2txt or userType == txt2ppo or userType == ppo2ppo):
	pass
else:
	sys.exit(m_error_userType)

# Ensures that the input file is of the right type
if ( userType == ppo2ppo and (check_if_xml in first_line_input)):
	pass
elif( (userType == txt2ppo or userType == txt2txt) and (check_if_xml in first_line_input)):
	sys.exit(m_invalid_input)
elif( (userType == txt2ppo or userType == txt2txt) and (check_if_xml not in first_line_input)):
	pass
else:
	#invalid input file
	sys.exit(m_invalid_input)

#
# ppo2ppo
#

if ( userType == ppo2ppo ):
	
	var = "VAR"
	aux = "AUX"
	con = "CON"
	obj = "OBJ"

	output_file = open(outPath, 'w')

	input_file = open(inPath, 'r').read()

	input_file = input_file.replace(optimization_end_tag, "")

	# XML reader part
	def xml2obj(src):
	    """
	    A simple function to converts XML data into native Python object.
	    """

	    non_id_char = re.compile('[^_0-9a-zA-Z]')
	    def _name_mangle(name):
	        return non_id_char.sub('_', name)

	    class DataNode(object):
	        def __init__(self):
	            self._attrs = {}    # XML attributes and child elements
	            self.data = None    # child text data
	        def __len__(self):
	            # treat single element as a list of 1
	            return 1
	        def __getitem__(self, key):
	            if isinstance(key, basestring):
	                return self._attrs.get(key,None)
	            else:
	                return [self][key]
	        def __contains__(self, name):
	            return self._attrs.has_key(name)
	        def __nonzero__(self):
	            return bool(self._attrs or self.data)
	        def __getattr__(self, name):
	            if name.startswith('__'):
	                # need to do this for Python special methods???
	                raise AttributeError(name)
	            return self._attrs.get(name,None)
	        def _add_xml_attr(self, name, value):
	            if name in self._attrs:
	                # multiple attribute of the same name are represented by a list
	                children = self._attrs[name]
	                if not isinstance(children, list):
	                    children = [children]
	                    self._attrs[name] = children
	                children.append(value)
	            else:
	                self._attrs[name] = value
	        def __str__(self):
	            return self.data or ''
	        def __repr__(self):
	            items = sorted(self._attrs.items())
	            if self.data:
	                items.append(('data', self.data))
	            return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])

	    class TreeBuilder(xml.sax.handler.ContentHandler):
	        def __init__(self):
	            self.stack = []
	            self.root = DataNode()
	            self.current = self.root
	            self.text_parts = []
	        def startElement(self, name, attrs):
	            self.stack.append((self.current, self.text_parts))
	            self.current = DataNode()
	            self.text_parts = []
	            # xml attributes --> python attributes
	            for k, v in attrs.items():
	                self.current._add_xml_attr(_name_mangle(k), v)
	        def endElement(self, name):
	            text = ''.join(self.text_parts).strip()
	            if text:
	                self.current.data = text
	            if self.current._attrs:
	                obj = self.current
	            else:
	                # a text only node is simply represented by the string
	                obj = text or ''
	            self.current, self.text_parts = self.stack.pop()
	            self.current._add_xml_attr(_name_mangle(name), obj)
	        def characters(self, content):
	            self.text_parts.append(content)

	    builder = TreeBuilder()
	    if isinstance(src,basestring):
	        xml.sax.parseString(src, builder)
	    else:
	        xml.sax.parse(src, builder)
	    return builder.root._attrs.values()[0]
	## end of http://code.activestate.com/recipes/534109/ }}}

	Optimization = xml2obj(open(inPath))
	Variable = Optimization.Variable
	total = len(Variable)
	line_num = 0
	function_num = 0
	var_list = []
	current_function = ""

	# defining all the variables in sympy
	while ( line_num != total ):
		if ( Variable[line_num].Role == var and Variable[line_num].Active == "false" ):
			# deactivated variable, skip it
			line_num = line_num + 1
			print "Skipped variable."
		elif ( Variable[line_num].Role == var ):
			current_line = str(Variable[line_num].Name)
			current_var = Symbol(current_line)
			var_list.append(current_var)
			print "Defined %s as variable" % (current_line)
			line_num = line_num + 1
		else:
			line_num = line_num + 1

	line_num = 0

	print >>output_file, input_file		

	# scanning through the functions and printing the derivatives
	while ( line_num != total ):
		if ( Variable[line_num].Active == "false" ):
			line_num = line_num + 1
			print "Skipped function."
		elif ( Variable[line_num].Role == aux ):
			print "pass"
			
			current_function = str(Variable[line_num].Equation)
			current_function = current_function.replace(exponent_pipeit, exponent_python)
			current_function_name = str(Variable[line_num].Name)
			line_num = line_num + 1
			for i in var_list:
				derivative = diff(current_function,i)
				print "Differentiated %s with respect to %s" % (current_function_name, i)
				derivative = str(derivative).replace(exponent_python, exponent_pipeit)

				if (derivative == 0):

					derivative_output = """
	<Variable Name="diff(%s,%s)"
	          Role="DER"
	          Type="REAL">
	<Equation Value="0"></Equation>
	</Variable>""" % (str(current_function_name).strip(), str(i).strip())

					print >>output_file, derivative_output

				else:
					derivative_output = """
	<Variable Name="diff(%s,%s)"
	          Role="DER"
	          Type="REAL">
	<Equation Value="">%s</Equation>
	</Variable>""" % (str(current_function_name).strip(), str(i).strip(), str(derivative).strip())

					print >>output_file, derivative_output
			
			line_num = line_num + 1
		elif ( Variable[line_num].Role == obj or Variable[line_num].Role == con ):
			current_function = str(Variable[line_num].Equation)
			current_function = current_function.replace(exponent_pipeit, exponent_python)
			current_function_name = str(Variable[line_num].Name)
			line_num = line_num + 1
			for i in var_list:
				derivative = diff(current_function,i)
				print "Differentiated %s with respect to %s" % (current_function_name, i)
				derivative = str(derivative).replace(exponent_python, exponent_pipeit)

				if (derivative == 0):

					derivative_output = """
	<Variable Name="diff(%s,%s)"
	          Role="DER"
	          Type="REAL">
	<Equation Value="0"></Equation>
	</Variable>""" % (str(current_function_name).strip(), str(i).strip())

					print >>output_file, derivative_output

				else:
					derivative_output = """
	<Variable Name="diff(%s,%s)"
	          Role="DER"
	          Type="REAL">
	<Equation Value="">%s</Equation>
	</Variable>""" % (str(current_function_name).strip(), str(i).strip(), str(derivative).strip())

					print >>output_file, derivative_output
		else:
			line_num = line_num + 1

	print >>output_file, optimization_end_tag
	print m_diff_complete
#
# txt2ppo
#
	
elif ( userType == txt2ppo ):
	
	start_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Optimization Version="1"
              DefaultSolver="Reflection"
              Direction="Max"
              MaxIter="100"
              Objective="None"
              RandomSeed="0"
              Solver="Reflection">
<Solver Name="Reflection">
</Solver>"""
	
	# Class to identify type(function or variable) and the equation
	class Line(object):
		def __init__(self, line):
			self.line = line
		def role(self):
			return self.line.split(":")[0]
		def whole(self):
			return self.line.split(":")[1]

	class Separator(object):
		def __init__(self, line):
			self.line = line
		def name(self):
			return self.line.split("=")[0]
		def equation(self):
			return self.line.split("=")[1]

	open(outPath, 'w').close()
	output_file = open(outPath, 'w')
	
	input_file = open(inPath,'r')

	total_lines = sum(1 for line in input_file)
	line_num = 1

	print >>output_file, start_xml

	#defining all the variables in sympy
	while ( line_num != total_lines + 1 ):
		current_line = linecache.getline(inPath, line_num)
		if ( Line(current_line).role().lower() == 'v' and ("=" in current_line)):
			current_line = Line(linecache.getline(inPath, line_num).strip()).whole()
			current_var = Symbol(current_line)
			sys.exit("ERROR: Define variable *%s* properly." % str(current_var).strip() )
			line_num = line_num + 1
		elif ( Line(current_line).role().lower() == 'v' ):
			current_line = Line(linecache.getline(inPath, line_num).strip()).whole()
			current_var = Symbol(current_line)

			current_var_output = """<Variable Name="%s"
          Role="VAR"
          Type="REAL"
          Lower="0"
          Value="0"
          Upper="0"/>""" % (str(current_var).strip())

			var_list.append(current_var)
			
			print m_variable_defined % (str(current_var).strip())

			print >>output_file, current_var_output

			line_num = line_num + 1
		else:
			line_num = line_num + 1

	line_num = 1

	# scanning through all the functions to print the derivatives 
	# with respect to every variable in order according to var_list
	while (line_num != total_lines + 1):
		current_line = linecache.getline(inPath, line_num)
		if (Line(current_line).role().lower() == "o" 
		or Line(current_line).role().lower() == "c" 
		or Line(current_line).role().lower() == "a"):

			# Getting the actual function, stripping the whitespace and replacing the pipe-it notation with python notation
			current_function = Separator(Line(linecache.getline(inPath, line_num).strip()).whole()).equation().replace(exponent_pipeit, exponent_python)
			current_function_name = Separator(Line(linecache.getline(inPath, line_num).strip()).whole()).name()

			if (Line(current_line).role().lower() == "o"):
				current_function_obj_output = """<Variable Name="%s"
          Role="OBJ"
          Type="REAL">
<Equation Value="0">%s</Equation>""" % (str(current_function_name).strip(), str(current_function).strip().replace(exponent_python, exponent_pipeit))

				print >>output_file, current_function_obj_output

			elif (Line(current_line).role().lower() == "c"):
				current_function_con_output = """<Variable Name="%s"
          Role="CON"
          Type="REAL">
<Equation Value="0">%s</Equation>""" % (str(current_function_name).strip(), str(current_function).strip().replace(exponent_python, exponent_pipeit))

				print >>output_file, current_function_con_output

			elif (Line(current_line).role().lower() == "a"):
				current_function_aux_output = """<Variable Name="%s"
          Role="AUX"
          Type="REAL">
<Equation Value="0">%s</Equation>""" % (str(current_function_name).strip(), str(current_function).strip().replace(exponent_python, exponent_pipeit))

				print >>output_file, current_function_aux_output

			else:
				break

				print >>output_file, current_function_obj_output

			for i in var_list:
				derivative = diff(current_function, i)
				
				print m_diff_with_respect_to % (str(current_function_name).strip(), str(i).strip())

				derivative_output_txt2ppo = """<Variable Name="diff(%s,%s)"
	          Role="DER"
	          Type="REAL">
<Equation Value="">%s</Equation>
</Variable>""" % (str(current_function_name).strip(), str(i).strip(), str(derivative).strip().replace(exponent_python, exponent_pipeit))

				print >>output_file, derivative_output_txt2ppo

			line_num = line_num + 1
		# if junk, skip line
		elif (colon not in current_line):
			line_num = line_num + 1
			print "Bad line. Skipped."

		else:
			line_num = line_num + 1

	print >>output_file, optimization_end_tag
	
	print m_diff_complete

#
# txt2txt
#
	
elif ( userType == txt2txt ):
	# Class to identify type(function or variable) and the equation
	class Line(object):
		def __init__(self, line):
			self.line = line
		def role(self):
			return self.line.split(":")[0]
		def whole(self):
			return self.line.split(":")[1]

	class Separator(object):
		def __init__(self, line):
			self.line = line
		def name(self):
			return self.line.split("=")[0]
		def equation(self):
			return self.line.split("=")[1]

	output_file = open(outPath, 'w')

	input_file = open(inPath,'r')

	total_lines = sum(1 for line in input_file)
	line_num = 1

	#defining all the variables in sympy
	while ( line_num != total_lines + 1 ):
		current_line = linecache.getline(inPath, line_num)
		if ( Line(current_line).role().lower() == 'v' and ("=" in current_line)):
			current_line = Line(linecache.getline(inPath, line_num).strip()).whole()
			current_var = Symbol(current_line)
			sys.exit("ERROR: Define variable *%s* properly." % str(current_var).strip() )
			line_num = line_num + 1
		elif ( Line(current_line).role().lower() == 'v' ):
			current_line = Line(linecache.getline(inPath, line_num).strip()).whole()
			current_var = Symbol(current_line)
			
			print m_variable_defined % (str(current_var).strip())
			
			var_list.append(current_var)
			line_num = line_num + 1
		else:
			line_num = line_num + 1

	line_num = 1

	# scanning through all the functions to print the derivatives 
	# with respect to every variable in order according to var_list
	while (line_num != total_lines + 1):
		current_line = linecache.getline(inPath, line_num)
		if (Line(current_line).role().lower() == "o" 
		or Line(current_line).role().lower() == "c" 
		or Line(current_line).role().lower() == "a"):
			# Getting the actual function, stripping the whitespace and replacing the pipe-it notation with python notation
			current_function = Separator(Line(linecache.getline(inPath, line_num).strip()).whole()).equation().replace(exponent_pipeit, exponent_python)
			current_function_name = Separator(Line(linecache.getline(inPath, line_num).strip()).whole()).name()
			for i in var_list:
				derivative = diff(current_function, i)
				
				print m_diff_with_respect_to % (str(current_function_name).strip(), str(i).strip())
				
				derivative_output_txt = "diff(%s,%s) = %s" % (str(current_function_name).strip(), str(i).strip(), str(derivative).strip().replace(exponent_python, exponent_pipeit))
				print >>output_file, derivative_output_txt
			line_num = line_num + 1
		# if junk, skip line
		elif (colon not in current_line):
			line_num = line_num + 1
			print "Bad line. Skipped."

		else:
			line_num = line_num + 1
	
	input_file.close()
	output_file.close()
	
	print m_diff_complete
	
else:
	print m_error_userType