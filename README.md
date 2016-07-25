# Differentiator Utility
(c) Petrostreamz 2012 http://www.petrostreamz.com
Author: Rafid Hoda

This utility takes an input file, either .ppo or txt and differentiates all the functions.

**Installation**

1. Copy Differentiator.exe Petrostreamz folder
2. Copy the contents of the Utilities folder to Petrostreamz/Utilities

**Usage**

With this utility you can take .txt or .ppo files containing functions and differentiate and output them to another .txt or .ppo file.

For ppo files you can use the Optimizer to edit the files and it will work with the utility.

For txt files, this is the notation you must use to define the functions and variables:

O: f1 = x + y
v: x
v: y

O is for "Objective function", f1 is the name of the function and x + y is the actual function. x and y are variables you must explicitly define.

Legend:

O: Objective
A: Auxiliary
C: Constraint
V: Variable

It does not matter if you use upper or lowercase.

**SymPy**
Copyright (c) 2006, 2007, 2008, 2009, 2010, 2011 SymPy Development Team

The libraries used to do the differentiation in this utility is developed by the SymPy Development Team.