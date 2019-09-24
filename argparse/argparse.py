"""
Minimal and functional version of CPython's argparse module.
"""

import sys


class Namespace:
    pass


class _ArgError(BaseException):
    pass


class _Arg:
    def __init__(self, names, dest, action, nargs, const, default, type, help):
        self.names = names
        self.dest = dest
        self.action = action
        self.nargs = nargs
        self.const = const
        self.default = default
        self.type = type
        self.help = help

    def parse(self, optname, eq_arg, args):
        # parse args for this arg
        if self.action == "store" or self.action == "append":
            if self.nargs is None:
                if eq_arg is not None:
                    ret = eq_arg
                elif args:
                    ret = args.pop(0)
                else:
                    raise _ArgError("expecting value for %s" % optname)
                return self.type(ret)
            elif self.nargs == "?":
                if eq_arg is not None:
                    ret = eq_arg
                elif args:
                    ret = args.pop(0)
                else:
                    return self.default
                return self.type(ret)
            else:
                if self.nargs == "*":
                    n = -1
                elif self.nargs == "+":
                    if not args:
                        raise _ArgError("expecting value for %s" % optname)
                    n = -1
                else:
                    n = int(self.nargs)
                ret = []
                stop_at_opt = True
                while args and n != 0:
                    if stop_at_opt and args[0].startswith("-") and args[0] != "-":
                        if args[0] == "--":
                            stop_at_opt = False
                            args.pop(0)
                        else:
                            break
                    else:
                        ret.append(args.pop(0))
                        n -= 1
                if n > 0:
                    raise _ArgError("expecting value for %s" % optname)
                return ret
        elif self.action == "store_const":
            return self.const
        else:
            assert False


def _dest_from_optnames(opt_names):
    dest = opt_names[0]
    for name in opt_names:
        if name.startswith("--"):
            dest = name
            break
    return dest.lstrip("-").replace("-", "_")


class ArgumentParser:
    def __init__(self, *, prog=None, description=""):
        self.prog = prog
        self.description = description
        self.opt = []
        self.pos = []

    def add_argument(self, *args, **kwargs):
        action = kwargs.get("action", "store")
        if action == "store_true":
            action = "store_const"
            const = True
            default = kwargs.get("default", False)
        elif action == "store_false":
            action = "store_const"
            const = False
            default = kwargs.get("default", True)
        elif action == "append":
            const = None
            default = kwargs.get("default", [])
        else:
            const = kwargs.get("const", None)
            default = kwargs.get("default", None)
        if args and args[0].startswith("-"):
            list = self.opt
            dest = kwargs.get("dest")
            if dest is None:
                dest = _dest_from_optnames(args)
        else:
            list = self.pos
            dest = kwargs.get("dest")
            if dest is None:
                dest = args[0]
            if not args:
                args = [dest]
        list.append(
            _Arg(args, dest, action, kwargs.get("nargs", None),
                 const, default, kwargs.get("type", str), kwargs.get("help", "")))

    def usage(self, full):
        # print short usage
        print("usage: %s [-h]" % self.prog or sys.argv[0], end="")

        def render_arg(arg):
            if arg.action == "store":
                if arg.nargs is None:
                    return " %s" % arg.dest
                if isinstance(arg.nargs, int):
                    return " %s(x%d)" % (arg.dest, arg.nargs)
                else:
                    return " %s%s" % (arg.dest, arg.nargs)
            else:
                return ""
        for opt in self.opt:
            print(" [%s%s]" % (', '.join(opt.names), render_arg(opt)), end="")
        for pos in self.pos:
            print(render_arg(pos), end="")
        print()

        if not full:
            return

        # print full information
        print()
        if self.description:
            print(self.description)
        if self.pos:
            print("\npositional args:")
            for pos in self.pos:
                print("  %-16s%s" % (pos.names[0], pos.help))
        print("\noptional args:")
        print("  -h, --help      show this message and exit")
        for opt in self.opt:
            print("  %-16s%s" % (', '.join(opt.names) + render_arg(opt), opt.help))

    def parse_args(self, args=None):
        return self._parse_args_impl(args, False)

    def parse_known_args(self, args=None):
        return self._parse_args_impl(args, True)

    def _parse_args_impl(self, args, return_unknown):
        if args is None:
            args = sys.argv[1:]
        else:
            args = args[:]
        try:
            return self._parse_args(args, return_unknown)
        except _ArgError as e:
            self.usage(False)
            print("error:", e)
            sys.exit(2)

    def _parse_args(self, args, return_unknown):
        argholder = Namespace()
        # add optional args with defaults
        for opt in self.opt:
            setattr(argholder, opt.dest, opt.default)

        # deal with unknown arguments, if needed
        unknown = []
        def consume_unknown():
            while args and not args[0].startswith("-"):
                unknown.append(args.pop(0))

        # parse all args
        parsed_pos = False
        while args or not parsed_pos:
            if args and args[0].startswith("-") and args[0] != "-" and args[0] != "--":
                # optional arg
                a = args.pop(0)
                if a in ("-h", "--help"):
                    self.usage(True)
                    sys.exit(0)

                eq_arg = None
                if a.startswith("--") and "=" in a:
                    a, eq_arg = a.split("=", 1)

                found = False
                for i, opt in enumerate(self.opt):
                    if a in opt.names:
                        val = opt.parse(a, eq_arg, args)
                        if opt.action == "append":
                            getattr(argholder, opt.dest).append(val)
                        else:
                            setattr(argholder, opt.dest, val)
                        found = True
                        break
                if not found:
                    if return_unknown:
                        unknown.append(a)
                        consume_unknown()
                    else:
                        raise _ArgError("unknown option %s" % a)
            else:
                # positional arg
                if parsed_pos:
                    if return_unknown:
                        unknown = unknown + args
                        break
                    else:
                        raise _ArgError("extra args: %s" % " ".join(args))
                for pos in self.pos:
                    setattr(argholder, pos.dest, pos.parse(pos.names[0], None, args))
                parsed_pos = True
                if return_unknown:
                    consume_unknown()

        return (argholder, unknown) if return_unknown else argholder
