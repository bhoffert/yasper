# yasper.py (Python3)
# Yasper - Yet Another Simple ParsER
#
# -- Purpose --
#
# Yasper is a simple parser designed for use in rapid prototyping and simple
# command-line utilities. With minimal setup, it allows the programmer to map
# keywords (commands) to functions in a single line of code.
#
# Example:
#   >>> yasper.registerFunction("add", lambda data: sum([int(x) for x in data]), -1)
#   >>> print(str(yasper.execute("add 2 4 6 8")))
#   20
#
# Yasper's command parsing is robust. It is able to match both under-typed and
# over-typed commands. For example, if the user defines the above "add" command,
# all of the following will execute the add command and return 20:
#   execute("ad 2 4 6 8")
#   execute("add 2 4 6 8")
#   execute("addf 2 4 6 8")
#
# In cases where the nearest command is ambiguous, Yasper prints an error.
#
# Note that commands are case-insensitive.
#
# -- Usage -- 
# 
# The parser is represented as a single Yasper object. All the programmer needs to
# access it is:
#   from yasper import Yasper
#
# Prior to use, the programmer must create the Yasper object:
#   yasper = Yasper()
#
# Functions are then fed to the parser object by using the registerFunction method:
#   yasper.registerFunction("command", func1, num_arguments)
#     
#         <"command">: The text command the user will type to call your function
#             <func1>: The actual function you are binding to the command
#     <num_arguments>: The number of arguments your function takes
#
# After you've fed the parser all of your functions, you must initialize your parser.
#   yaser.initialize()
#
# Initializing the parser causes it to build the command lookup tree so that it can
# recognize all of the commands you've defined. Failing to initialize the parser will
# cause your code to throw errors.
#
# Once the parser is initialized, you can parse and execute any input string:
#   execute("input string")
# 
# The parser always interprets the first word as the command and all subsequent words
# as arguments to the command. It will throw out any extra arguments not used by the
# function.
#
# -- Defining Functions --
# 
# Functions used with yaser must follow a single important requirement: They must take
# a single parameter, <data>, which is a list of strings. Each string in data is an
# argument to the function. You must convert the data from its string format in the body
# of your functino.
#
# Based on the num_arguments you specify when you register the function, Yasper
# guarantees that your function receives the correct number of arguments. If
# num_arguments == 0, then data will be an empty list []. If num_arguments == 2, then
# data will be a list with two elements. A special case is when you specify that
# num_arguments is negative; in that case, data can be of any length. This is useful
# if you want your function to take a variable number of arguments or if you're
# prototyping and don't yet need the strict argument number checking.
#
# If a string executed doesn't have enough arguments for its command, Yasper will print
# an error and never call the function. If it has too many arguments, it will only pass
# the function the first <x> number of arguments received, where <x> = num_arguments.
#
# -- Missing Features --
#
# The following features are high-priority TODO items:
#   * Allow the programmer to toggle under-matching and over-matching for 
#     sensitive applications


class Yasper:
    """The parser imported by the programmer.

    Public methods:
        __init__ -- Class constructor, takes no arguments.
        registerFunction -- Fully specifies a function to be used by the parser.
        initialize -- Called after all functions are registered; builds command parser.
        execute -- Called on any string the programmer wants to parse; may return a
                   value.

    Private methods:
        callFunction -- "Physically" calls the function corresponding to the command
                        with the data as an argument.
        getCommand -- Begins the search for the command in the command search tree.

    Private fields:
        fdict -- The dictionary that matches a command(string) to its actual function
                 code (first-class object).
        ctree -- The search tree that matches a user-typed command to a real one.
    """
    def __init__(self):
        """Initializes the parser with an empty function dictionary."""
        self.fdict = {}
        # TODO: Allow for shared data between functions
        # self.fdata = {}

    def registerFunction(self, s, f, nargs):
        """Record a command-function pair in fdict.

        Args:
            s (str): The text command that will call the function.
            f (func): The function to be called on-command.
            nargs (int): The number of arguments the function expects to take.
        """
        # Function keys are case-insensitive; they're stored uppercase
        self.fdict[s.upper()] = YasperFunction(f, nargs)

    def callFunction(self, s, data):
        """Call the function, corresponding to the command, with data as the argument.

        Args:
            s (str): The key for fdict that matches the function to be called.
            data (list[str]): The arguments to be passed to the function.

        Returns:
            The return value of the function that is called.
            Will always return None if the length of the list of arguments doesn't
              match the number of arguments expected by the function.
        """
        expectednargs = self.fdict[s].nargs
        if len(data) >= expectednargs:
            # Ignore expectedargs if it's negative, which signals arbitrary length
            if expectednargs >= 0:
                data = data[:expectednargs]
        else:
            errorprint("Too few arguments for command " + s)
            return
        func = self.fdict[s].f
        return (self.fdict[s].f)(data)

    def execute(self, inputstring):
        """Convert the string to be parsed into code to be executed.

        Args:
            inputstring (str): The user input that needs to be parsed and executed.

        Returns:
            The eventual return value of whatever function the inputstring calls.
            Will always return None if there is an error.
        """
        if inputstring == "":
            return
        inputlist = inputstring.split()
        # The command is always the first entry in the string and is case-insensitive
        command = self.getCommand(inputlist[0].upper())
        if command is None:
            errorprint("Invalid or ambiguous command")
            return
        # TODO: Incorporate #args to allow multiple commands at once
        return self.callFunction(command, inputlist[1:])

    def initialize(self):
        """Create the command search tree that will identify a command that was registered
        with the parser. The keys from fdict are the commands.
        """
        self.ctree = YasperCommandTree()
        commands = self.fdict.keys()
        self.ctree.initialize(commands)

    def getCommand(self, s):
        """Launche the search for a command in the command search tree.

        Args:
            s (str): The input that needs to be matched to a command.

        Returns:
            A key for fdict, if a matching command was found.
            None, if no matching command was found.
        """
        return self.ctree.getCommand(s)

class YasperFunction:
    """A container that pairs together a function and its number of arguments."""
    def __init__(self, f, nargs):
        """Constructor.

        Args:
            f (func): The callable function.
            nargs (int): The number of arguments f expects
        """
        self.f = f
        self.nargs = nargs

class YasperCommandTree:
    """The command search tree.

    Public methods:
        __init__ -- Constructor, takes no arguments
        initialize -- Constructs the tree from a list of commands; must be called
                      before the tree can be used
        getCommand -- Searches for a matching command given a string

    Private fields:
        root (YaserCommandTreeNode) -- The root of the search tree; corresponds
                                       to the empty string
    """
    def __init__(self):
        """Constructor. Creates the root node from which the tree will grow."""
        self.root = YasperCommandTreeNode('')

    def initialize(self, commandlist):
        """Grow the tree from a list of commands.

        Args:
            commandlist (list[str]): A list of valid commands.
        """
        for command in commandlist:
            self.root.addCommand(command)
        # Nodes' maxdescendants fields must be updated after filling the tree
        self.root.updateMaxDescendants()

    def getCommand(self, s):
        """Attempt to match an input string to a command in the tree.

        Args:
            s (str): The input that should be matched to a command.

        Returns:
            A valid command, if one could be matched to s.
            None, if no valid command could be matched to s.
        """
        return self.root.searchCommand(s)

class YasperCommandTreeNode:
    """A node in the YasperCommandTree.

    Public methods:
        __init__ -- Constructor; takes a character that represents the node.
        addCommand -- Adds a command string to the tree and marks it as valid.
        searchCommand -- Given a string, finds a valid command in the tree.
        updateMaxDescendants -- updates the maxdescendants field for this node
                                and all children nodes.
    
    Private methods:
        addchild -- Adds a child node that represents the given character.
        getChild -- Returns a child node that represents the given character.
        followTrail -- Follows/returns a deterministic path to a descendant leaf.
    
    Private fields:
        c -- The character this node represents.
        children -- The list of this node's children nodes.
        terminal -- Boolean: does this node represent the final character in a 
                   command?
        maxdescendants -- That maximum number of children this node or any
                          descendant node has.
    """
    def __init__(self, c):
        """Constructor; create a node that represents a character.

        Also initializes all private fields to their default/empty values.

        Args:
            c (str): One-character string that this node will represent.
        """
        self.c = c
        self.children = YasperCommandTreeNodeChildren()
        self.terminal = False
        self.maxdescendants = 0

    def addChild(self, c):
        """Add a new node that represents a character to this node's children.

        Args:
            c (str): The one-character string that should be represented.

        Returns:
            The node added."""
        return self.children.addChild(c)

    def getChild(self, c):
        """Return a child node that represents the given character.

        Args:
            c (str): The one-character string that should be represented.

        Returns:
            A child node representing c, if one is found.
            None, if no child node representing c is found.
        """
        return self.children.getChild(c)

    def updateMaxDescendants(self):
        """Recursively update this node and all children node with the maximum
        number of children found for any node or its children nodes.

        Returns:
            This node's maximum descendants, an integer.
        """
        maxofchildren = 0
        for child in self.children:
            maxofchildren = max(maxofchildren, child.updateMaxDescendants())
        self.maxdescendants = max(len(self.children), maxofchildren)
        return self.maxdescendants

    def addCommand(self, s):
        """Recursively add a command to the subtree with this node as root.

        Args:
            s (str): The command to be added. Note that this is usually a partial
                     command, characters from ascendants trimmed off.
        """
        # Empty string means this is the final character in the string
        if s == "":
            self.terminal = True
            return
        nextnode = self.getChild(s[0])
        # If there is no child representing the next character in the command,
        # create it. Then, continue adding the command starting at the next
        # letter in the command.
        if nextnode is None:
            nextnode = self.addChild(s[0])
        nextnode.addCommand(s[1:])

    def searchCommand(self, s):
        """Recursively search for a command in the subtree with this node as root.

        Args:
            s (str): The command to be matched. Note that th is is usually a partial
                     command, characters from ascendants trimmed off.

        Returns:
            A string matching the command found in this node or its descendants, if
              one is found.
            None, if no match is found in this command or its descendants.
        """
        # If the string is empty, return the current command or one that can be matched
        # in descendants without any ambiguity
        if s == "":
            if self.terminal == True:
                return self.c
            if self.maxdescendants == 1:
                return self.followTrail()
            return None
        nextnode = self.children.getChild(s[0])
        # If the string continues but we can't find it in descendants, then return
        # the current command if we've formed one, or return None if we haven't
        if nextnode is None:
            if self.terminal == True:
                return self.c
            return None
        futuresearch = nextnode.searchCommand(s[1:])
        # Only return a path if we found a match in our recursive search
        if futuresearch is None:
            return None
        return self.c + futuresearch

    def followTrail(self):
        """Recursively follow and return the deepest deterministic path
        through descendants.

        Returns:
            The determinist path (string) from this node through its descendants,
              if there is one.
            None if there is no deterministic path.
        """
        if len(self.children) == 1:
            if self.terminal == True:
                # Ambiguous because trail could stop here or continue
                return None
            subtrail = self.children[0].followTrail()
            if subtrail is None:
                # Subtrail is ambiguous
                return None
            return self.c + subtrail
        return self.c

class YasperCommandTreeNodeChildren:
    """A list of YasperCommandTreeNodeChildren with some convenience methods.

    TODO: Refactor this to extend built-in list, if possible?

    Public methods:
        __init__ -- Constructor; takes no arguments.
        __len__ -- len() compatibility
        __iter__ -- iterator compatibility
        __getitem__ -- [index] compatibility
        __setitem__ -- [index] compatibility
        getCharacters -- Get a list of characters represented by nodes in the list.
        addChild -- Creates and adds a node representing a character to the list.
        getChild -- Lookup (return) a node that represents a given character.

    Private fields:
        childrenlist -- A list of YasperCommandTreeNode 
    """
    def __init__(self):
        """Constructor; creates an empty list."""
        self.childrenlist = []

    def __len__(self):
        """Return length of list field."""
        return len(self.childrenlist)

        """Return an iterator for list field."""
    def __iter__(self):
        return iter(self.childrenlist)

    def __getitem__(self, index):
        """Return item of list field at given index."""
        return self.childrenlist[index]

    def __setitem__(self, index, x):
        """Set item of list field at given index."""
        self.childrenlist[index] = x

    def getCharacters(self):
        """Convert the list field into the list of the characters it represents."""
        charlist = []
        for child in self.childrenlist:
            charlist.append(child.c)
        return charlist

    def addChild(self, c):
        """Add a new node to the list that represents the given character.

        Args:
            c (str): Single-character string that the new node represents.

        Returns:
            The node added, if no node representing that character was in the list.
            The node in the list representing that character, if already present.
        """
        newnode = None
        if c in self.getCharacters():
            newnode = self.getChild(c)
        else:
            newnode = YasperCommandTreeNode(c)
            self.childrenlist.append(newnode)
        return newnode

    def getChild(self, c):
        """Check the nodes in the list to see if any represent the given character.

        Args:
            c (str): Single-character string to check if any nodes represent.

        Returns:
            The node representing c, if present in the list.
            None, if no node in the list represents c.
        """
        for child in self.childrenlist:
            if child.c == c:
                return child
        return None

def errorprint(es):
    """Print the error string 'es'."""
    print("ERROR: " + es)