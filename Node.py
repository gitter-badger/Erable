from __future__ import print_function,division,absolute_import

import copy
import Exceptions


def arrToStr(arr):
	''' an tool function which turns list-fied string back to the string '''
	string=""
	for c in arr:
		string+=c
	return string
def matchStart(arr,s):
	'''match string at start'''
	if len(s)>0:
		for b in arr:
			# print("COMPARING %s WITH %s"%(arrToStr(s),b))
			if arrToStr(s).startswith(b):
				return True
	return False
nddata={
	"isValid":"isValid",
	"isList" :"isList",
	"isBlock":"isBlock",
	"length" :"length",
	"restStr":"restStr"
}

'''Identifiers used for variable declaration'''
var_identifiers=["let","const","var","ref","obj","changable"]
'''Identifiers used for if statement'''
if_identifiers=["if","elif","else"]

'''
basic operations
'''
basic_operations=[
	"return ",
	"delete ",
	"emit "  
]

'''
Unary  Operations
'return': return value
'!'     : not gate
'@'     : gets the value by the reference
'#'     : gets the reference by the value
'''
unary_operations=[
	*basic_operations,
	"!",
	"@","#"
]

'''
Binary Operations
"a<<<b": unsigned a<<b
"a>>>b": unsigned a>>b
"a<=>b": swap a and b (value type must be same)
"a==b" : decides if a equals b
"a!=b" : decides if a does not equal to b
"a<=b" : decides if a is less than or equal to b
"a>=b" : decides if a is greater or equal to b
"a>>b" : move b binary digit right of a
"a<<b" : move b binary digit left of a
"a&&b" : boolean a and b
"a||b" : boolean a or b
"a.b"  : gets the field b of a
"a+b,a-b,a*b,a/b,a%b": do calculation
"a&b"  : binary a and b
"a|b"  : binary a or b
"a^b"  : binary a xor b
"a=b"  : change the value of a to b
"a>b,a<b" : decides if a is greater than/less than b
":"    : TODO
"?"    : TODO
'''
binary_operations=[
	"<<<",">>>","<=>",
	"==","!=","<=",">=","<<",">>","&&","||",
	".","+","-","*","/","%","&","|","^","=",">","<",":","?"
]
evaluation_operations=["+","-","*","/","%"]

'''digits'''
nums=list("0123456789abcdef")

class Code:
	'''I dont know what this is for'''
	source="None"
	tokens=[]
	cls=None
	@classmethod
	def proc(*args):
		pass
	@classmethod
	def getValue(*args):
		pass

class StringCode(Code):
	'''neither this'''
	def __init__(self,string):
		self.source='"%s"'(string)
		self.tokens=['"',string,'"']

class NodeData:
	'''Stores the data returned from the syntax parser(Node)'''
	def __init__(self,
				value=None,
				type="null",
				cls="null",
				err=None,
				length=0,
				restStr="",
				needsAdd=True,
				*args,
				**kwargs):
		self.value=value
		self.type=type
		self.cls=cls
		self.err=err
		self.restStr=restStr
		self.needsAdd=needsAdd
		self.data=kwargs
		self.arr=list(args)
		if self.data.get("isValid") == None:
			self.data["isValid"]=True
	def __str__(self):
		return str(vars(self))

class InstanceNodeData(NodeData):
	'''
		Base Class for instance types
	'''
	def __init__(self,value=None,cls="null",restStr="",*args,**kwargs):
		NodeData.__init__(self,value=value,type="instance",cls=cls,restStr=restStr,*args,**kwargs)

class StringNodeData(InstanceNodeData):
	'''
		NodeData for string
	'''
	def __init__(self,string,restStr):
		InstanceNodeData.__init__(self,string,cls="string",restStr=restStr)

class NumNodeData(InstanceNodeData):
	'''
		NodeData for numbers
	'''
	def __init__(self,num,restStr):
		InstanceNodeData.__init__(self,num,cls="number",restStr=restStr)

class UnaryOperation(NodeData):
	'''
		NodeData class to store unary operations
	'''
	def __init__(self,operation,target,restStr):
		NodeData.__init__(self,None,type="operation",cls=operation,restStr=restStr)
		self.data["target"]=target

class BinaryOperation(NodeData):
	'''
		NodeData class to store binary operations
	'''
	def __init__(self,operation,target,field,restStr):
		NodeData.__init__(self,None,type="operation",cls=operation,restStr=restStr,needsAdd=False)
		self.data['target']=target
		self.data['field']=field

class ExprNodeData(NodeData):
	'''
		expr Node data
	'''
	def __init__(self,
				value=None,
				cls="null",
				err=None,
				length=0,
				restStr="",
				*args,
				**kwargs):
		NodeData.__init__(self,value,type="expr",cls=cls,err=err,length=length,restStr=restStr,*args,**kwargs)
class IfNodeData(ExprNodeData):
	def __init__(self,cls="null",cond=None,do=None,restStr=""):
		ExprNodeData.__init__(self,None,cls=cls,restStr=restStr)
		self.cond=cond
		self.do=do
		self.elses=[]
		self.elifs=[]
class Node:		
	'''Basic Node Class'''
	@classmethod
	def __init__(self):
		pass
	@classmethod
	def valid(self,s):
		'''Used to check if the syntax is valid.'''
		return True
	@classmethod
	def process(self,s):
		''' 
			usally called when the syntax is valid.
			processes the code and give the result as a NodeData
		'''
		nd= NodeData('',restStr=s)
		return nd
	@classmethod
	def bind(self,node):
		'''Binds the parent'''
		# bind the parent node
		self.parent=node
class WhitespaceNode(Node):
	'''Used to Ignore Whitespaces'''
	def valid(self,s):
		return len(s)>0 and s[0].isspace()
	def process(self,s):
		for c in copy.deepcopy(s):
			if c.isspace():
				s.remove(s[0])
			else:
				break
		return ExprNodeData(None,restStr=s,cls="whitespace")

class SplitNode(Node):		
	'''Used to process split.'''
	def valid(self,s):
		if len(s)>0:
			return s[0]==';'
		return False
	def process(self,s):
		if len(s)>0:
			for c in copy.deepcopy(s):
				if c==';':
					s.remove(s[0])
				else:
					break
			'''
				start a new line of code
			'''
			self.parent.coden+=1
			self.parent.codebuf.append([])
			self.parent.current=None
		return ExprNodeData(restStr=s,cls="split")

class CommaNode(Node):		
	'''Used to ignore commas or used in argument parsing'''
	def valid(self,s):
		if len(s)>0:
			return s[0]==','
		return False
	def process(self,s):
		if len(s)>0:
			for c in copy.deepcopy(s):
				if c==',':
					s.remove(s[0])
				else:
					break
		return ExprNodeData(restStr=s,cls="comma")

class NameNode(Node):
	'''Basic Name Structure.regex:  [a-zA-Z_$][a-zA-Z0-9_$]*'''
	def valid(self,s):
		isValid=True
		if len(s)>0 :
			if s[0].isdigit() or (not s[0].isalpha()) and not s[0] in list("_$"):
				isValid=False
				return False
		else:
			isValid=False
		return isValid
	def process(self,s):
		res=''
		if len(s)>0:
			if s[0].isdigit():
				Exceptions.exception(message="name cannot be started with a digit").throw()
		for c in copy.deepcopy(s):
			if not c.isalpha() and not c in list("_$") and not c.isdigit():
				break
			res+=c
			s.remove(s[0])
		
		return ExprNodeData(res,cls="name",length=len(res),isValid=True,restStr=s)


class NumNode(Node):
	'''
		Processes Numbers
		radix changed when using:
			char | radix
			t    |     2
			o    |     8
			p    |    10
			x    |    16
	'''
	def valid(self,s):
		if len(s)>0:
			if s[0].isdigit():
				return True
		return False
	def process(self,s):
		orig=copy.deepcopy(s)
		res=0
		radix=10
		if len(s)>0:
			for c in copy.deepcopy(s):
				if c=='x':
					radix=16
				elif c=='o':
					radix=8
				elif c=='t':
					radix=2
				elif c=='p':
					radix=10
				else:
					if c in nums:
						print("found %s in nums"%(c))
						if nums.index(c)<radix:
							res*=radix
							res+=nums.index(c)
						else:
							Exceptions.exception(message="Number '%d' is not in radix '%d'"%(nums.index(c),radix),stack=[Exceptions.stack(self.
							parent.line,self.parent.column,orig)]).throw()
					else:
						break
				s.remove(s[0])
		return NumNodeData(res,restStr=s)

class StringNode(Node):		
	'''Processes Strings'''
	def valid(self,s):
		if len(s)<=0:
			return False
		if s[0] is not '"':
			return False
		started=False
		for c in s:
			if c=='"':
				started=not started
				# one round detecting string is over.
				if not started:
					return True
		return False
	def process(self,s):
		started=False
		ret=''
		for c in copy.deepcopy(s):
			if c is '"':
				started=not started
				if not started:
					s.remove(s[0])
					return StringNodeData(ret,restStr=s)
			else:
				ret+=c
			s.remove(s[0])
		Exceptions.exception(message="Error:Unterminated String Literal").throw()


class CodeBlockNode(Node):
	'''
		Processes the code blocks
		{
			[codes]
		}
		(
			[codes]
		)
	'''
	def valid(self,s):
		if len(s)>0:
			if s[0] in ["{","("]:
				return True
		return False
	def process(self,s):
		if len(s)>0:
			# codes inside the code block
			cbk=""
			# level of the scope
			which=0
			for c in copy.deepcopy(s):
				s.remove(s[0])
				if c in ['{','(']:
					which+=1
					if which!=1:
						cbk+=c
					continue
				elif c in ['}',')']:
					which-=1
					if which==0:
						break
					else:
						cbk+=c
					continue
				cbk+=c
			print("---CODE BLOCK---")
			print(cbk)
			print("---END CODE BLOCK---")
			blk=[[]]
			pcs=Processor()
			blk=pcs.process(cbk)
			return ExprNodeData(value=blk,cls="codeblock",restStr=s)

class VarNode(Node):			
	'''
		Processes Variable Declaration
		(var|let|const|changable|obj|ref)+ NameNode [= ExprNode]
			var      : global
			let      : only in current scope or deeper
			const    : not changable
			changable: changanle
			obj      : it specifies that the value is an object
			ref      : it specifies that the value points to an object
		NOTE : reference can also be stored as a value,but it comes out as a number.
	'''
	def valid(self,s):
		isOk=False
		word=''
		for c in s:
			word+=c
			if word in var_identifiers:
				return True
		return False
	def process(self,s):
		ids=[]
		globn=NameNode()
		wn=WhitespaceNode()
		while globn.valid(s):
			globnd=globn.process(s)
			s=globnd.restStr
			s=wn.process(s).restStr
			ids.append(globnd.value)
		changable= "const" in ids
		glob= "var" in ids
		glob= not ("let" in ids)
		isref="ref" in ids
		finalIdentifiers=[]
		if changable:
			finalIdentifiers.append("const")
		else:
			finalIdentifiers.append("changable")
		if glob:
			finalIdentifiers.append("var")
		else:
			finalIdentifiers.append("let")
		if isref:
			finalIdentifiers.append("ref")
		else:
			finalIdentifiers.append("obj")
		fnd=ExprNodeData(None,cls="var",identifiers=finalIdentifiers)
		varname='unknown_variable'
		if len(ids)>0:
			if ids[len(ids)-1] in var_identifiers:
				Exceptions.exception(name="SyntaxError",message="Expected Variable Name but got Identifiers.").throw()
			else:
				varname=ids[len(ids)-1]
		else:
			Exceptions.exception(message="How did you do it...").throw()
		if len(s)>0:
			if s[0] == '=':
				s.remove(s[0])
				en=ExprNode()
				en.bind(self.parent)
				if en.valid(s):
					end=en.process(s)
					s=end.restStr
					if end.err is not None:
						raise end.err
					if end.data["isValid"]:
						fnd.value=end
					else:
						Exceptions.exception(message="Syntax error:expression not valid").throw()
				else:
					Exceptions.exception("Syntax error:expression not valid").throw()
		fnd.data["key"]=varname
		fnd.restStr=s
		return fnd

class FuncCallNode(Node):		
	'''
		Processes a function calling
		[NameNode] ([ExprNode[,ExprNode[,...]]])
	'''
	def valid(self,s):
		for c in s:
			if c=='(':
				return True
			if c.isspace() or not c.isalpha() and not c.isdigit() and not c=='(':
				return False
		return False
	def process(self,s):
		cct=''
		if len(s)>0:
			args=''
			funcName=''
			isInArgs=0
			isInStr=False
			nn=NameNode()
			nn.bind(self.parent)
			nnd=nn.process(s)
			funcName=nnd.value
			s=nnd.restStr
			aargs=[]
			rargs=[]
			if s[0]=='(':
				isInArgs+=1
				s.remove(s[0])
				for c in copy.deepcopy(s):
					cct+=c
					s.remove(s[0])
					if c=='(':
						if not isInStr:
							isInArgs+=1
					if c==')':
						if not isInStr:
							isInArgs-=1
							if isInArgs==0:
								if args!="":
									aargs.append(args)
									args=""
								break
					if c=='"':
						isInStr=not isInStr
					if isInArgs>0:
						args+=c
					if isInArgs==1 and c==',':
						aargs.append(args)
						args=""
				for arg in aargs:
					pcs=Processor()
					cbf=pcs.process(arg)[0]
					rargs.append(cbf)
				return ExprNodeData(value=funcName,cls="funccall",restStr=s,arguments=rargs)
			else:
				return 	ExprNodeData(value=funcName,cls="funccall",restStr=s,arguments=[])
			if isInArgs:
				Exceptions.exception(message="Unterminated argument value passing.",stack=[Exceptions.stack(line=self.parent.line,column=self.parent.column,code=cct)]).throw()
			print("FINAL ARGS:",args)
					
		return NodeData(value=None,type="expr",cls="funccall",restStr=s,arguments=aargs,funcName=funcName)
		

class NewNode(Node):
	'''
		processes an initialisation.
		Usage:
			new [FuncCallNode]
		NOTE : you can also use 'new cls' instead of 'new cls()'
	'''
	def valid(self,s):
		if len(s)>=3:
			return s[0:3]==list("new")
	def process(self,s):
		cct='' # string read and concated.
		if len(s)>0:
			s=s[4:]
			retn=ExprNodeData(value=None,cls="new")
			
			fcn=FuncCallNode()
			fcn.bind(self.parent)
			fcnd=fcn.process(s)
			printf(fcnd)
			s=fcnd.restStr
			retn.value=fcnd.value
			retn.restStr=s
			retn.data['arguments']=fcnd.data["arguments"]
			return retn
		Exceptions.EOFException().throw()


class BinaryOpNode(Node):
	'''
		processes binary opreations
		[ExprNode] [bin_op] (FuncCallNode|NameNode)
	'''
	def valid(self,s):
		return matchStart(binary_operations,s)
	def process(self,s):
		currentab=self.parent.codebuf[self.parent.coden]
		if len(currentab)<1:
			Exceptions.exception(name="SyntaxError",message="using binary operation after nothing",stack=[Exceptions.stack(line=self.parent.line,column=self.parent.column,code=s)]).throw()
		currenta=self.parent.current
		current=None
		types=[]
		en=ExprNode()
		en.bind(self.parent)
		op="null"
		stringified=arrToStr(s)
		for it in binary_operations:
			if stringified.startswith(it):
				op=it
				break
		s=s[len(op):]
		if currenta.cls=="var":
			current=currenta.value
		else:
			current=currenta
		ccp=current
		if op in ["*","/","%"] and current.type=="operation":
			print("CHANGING ORDER OF OPERATION...")
			if current.cls in binary_operations:
				current=current.data['field']
			elif current.cls in unary_operations:
				current=current.data["target"]
			else:
				Exceptions.exception(name="OperationNotFoundError",message="unknown operation for matching.",stack=[Exceptions.stack(line=self.parent.line,column=self.parent.column,code=s)]).throw()
		cpy=copy.deepcopy(current)
		current.value=None
		current.type="operation"
		current.cls=op
		print("---processing field after binary operator '%s'....---"%(op))
		end=en.process(s)
		print("---DOT EXPR PROCESSED---\n")
		s=end.restStr
		ccp.restStr=s
		current.data["field"]=end
		current.data["target"]=cpy
		current=ccp
		current.needsAdd=False
		return current
	
class UnaryOpNode(Node):
	'''
		processes unary opreations
		[ExprNode] [unary_op] (FuncCallNode|NameNode)
	'''
	def valid(self,s):
		return matchStart(unary_operations,s) and not matchStart(binary_operations,s)
	def process(self,s):
		types=[]
		en=ExprNode()
		en.bind(self.parent)
		op="null"
		stringified=arrToStr(s)
		for it in unary_operations:
			if stringified.startswith(it):
				op=it
				break
		s=s[len(op):]
		if op in basic_operations:
			op=op[:-1]
		print("---processing field after unary operator '%s'....---"%(op))
		end=en.process(s)
		print("---DOT EXPR PROCESSED---\n")
		s=end.restStr
		current=UnaryOperation(op,end,s)
		return current

class IfNode(Node):
	'''TODO:all stuff related to if statement'''
	def valid(self,s):
		for i in if_identifiers:
			if arrToStr(s).startswith(i+"(") or arrToStr(s).startswith(i+"{"):
				return True
		return False
	def process(self,s):
		cls="null"
		for i in if_identifiers:
			if arrToStr(s).startswith(i):
				cls=i
		if cls=="null":
			Exceptions.exception(message="Not a valid if statement",stack=[Exceptions.stack(line=self.parent.line,column=self.parent.column,code=s)]).throw()
		print("IF STATE MENT '%s' FOUND"%(cls))
		s=s[len(cls):]
		cbn=CodeBlockNode()
		# cbn.bind(self.parent)
		cond=None
		if cls!="else":
			cond=cbn.process(s)
			s=cond.restStr
		dosth=cbn.process(s)
		s=dosth.restStr
		ifnd=IfNodeData(cls=cls,cond=cond,do=dosth,restStr=s)
		if cls=="if":
			return ifnd
		else:
			current=self.parent.current
			if current.cls in if_identifiers and cls!="if":
				ifnd.needsAdd=False
				if cls=="else":
					current.elses.append(ifnd)
				elif cls=="elif":
					current.elifs.append(ifnd)
				else:
					Exceptions.exception(message="undefined class of if statement").throw()
				return ifnd
			else:
				Exceptions.exception(message="Undefined Behavior").throw()
		Exceptions.exception(message="unknown").throw()
	

exprs=[
	BinaryOpNode,
	UnaryOpNode,
	CodeBlockNode,
	VarNode,
	IfNode,
	StringNode,
	NumNode,
	NewNode,
	FuncCallNode,
	NameNode,
	WhitespaceNode,
	SplitNode,
	CommaNode
]
dot_exprs=[
	FuncCallNode,
	NameNode
]	
class ExprNode(Node):
	nodes=exprs
	
	def __init__(self,nodes=exprs):
		self.nodes=nodes
		
	
	def valid(self,s):
		for n in self.nodes:
			if n().valid(s):
				print("%s is valid with %s"%(n,str(s)))
				return n
		return False
	def process(self,s):
		for n in self.nodes:
			ins=n()
			if ins.valid(s):
				ins.bind(self.parent)
				nr=ins.process(s)
				if nr.needsAdd:
					self.parent.current=nr
					print("---CURRENT :",hex(id(self.parent.current)),"---")
					printf(self.parent.current)
					print('---END CURRENT---')
				return nr
			
		Exceptions.exception(message="Unknown Syntax",stack=[Exceptions.stack(self.parent.line,self.parent.column,s)]).throw()

class Processor:
	
	def __init__(self):
		self.codebuf=[[]]
		self.isInArgs=False
		self.current=None
		self.en=ExprNode()
		self.line=1
		self.column=1
		self.coden=0
		self.en.parent=self
	def process(self,inp):
		length=len(inp)
		while len(inp)>0:
			vld=self.en.valid(inp)
			if vld:
				print("VALID:",vld.__name__)
			else:
				print("NO VALID EXPR!")
			end=self.en.process(list(inp))
			print("---NEW CURRENT---")
			print(self.current)
			print("---END NEW CURRENT---")
			inp=end.restStr
			self.column+=length-len(inp)
			length=len(inp)
			if not end.needsAdd:
				print(end.cls,": ")
				printf(self.current)
				print("")
				continue
			elif end.cls in ["split","comma","whitespace"]:
				print(end.cls,"MET")
				continue
			self.codebuf[self.coden].append(end)
			
			printf(end)
			print("one code ended")
		self.line+=1
		self.column=1
		return self.codebuf
		
		
		
def printf(s):
	print(s)
print("LeafLang Testing")
inp=input('>')
proc=Processor()
while inp is not 'quit()':
	res=proc.process(list(inp))
	for i in res:
		print('[')
		for j in i:
			print('      ',j.__str__())
		print(']')
	inp=input('>')
