import argparse
import random
import sys
import time


def bubble_sort(list_):
    n = len(list_)
    for k in range(1, n):
        for i in range(n - k):
            if list_[i] > list_[i+1]:
                list_[i], list_[i+1] = list_[i+1], list_[i]

    return list_


def cocktail_sort(list_):
    """bubble sort but in both directions"""
    n = len(list_)
    for k in range(1, n):
        #from left to right
        for i in range(k - 1, n - k):
            if list_[i] > list_[i+1]:
                list_[i], list_[i+1] = list_[i+1], list_[i]
        #from right to left
        for i in reversed(range(k, n - k)):
            if list_[i] < list_[i-1]:
                list_[i], list_[i-1] = list_[i-1], list_[i]

    return list_


def merge_sort(list_):

    def merge(list1, list2):
        out = []
        append = out.append
        extend = out.extend
        n1, n2 = len(list1), len(list2)
        i, j = 0, 0
        while i < n1  or j < n2:
            if i < n1:
                obj1 = list1[i]
            else:
                extend(list2[j:])
                break

            if j < n2:
                obj2 = list2[j]
            else:
                extend(list1[i:])
                break

            if obj1 <= obj2:
                append(obj1)
                i += 1
            if obj2 < obj1:
                append(obj2)
                j += 1
        return out
            

    def divide(list_):
        n = len(list_)
        if n == 1:
            return list_
        else:
            half = int(n/2)
            list1 = divide(list_[:half])
            list2 = divide(list_[half:])
            return merge(list1, list2)

    return divide(list_)


class Tester:
    """Based on https://chase-seibert.github.io/blog/2014/03/21/python-multilevel-argparse.html#"""
    def __init__(self, available_methods):
        self.available_methods = available_methods
        parser = argparse.ArgumentParser(
            description='Test sorting algorthms',
            usage='''sorting.py <command> [<args>]

                There are two commands:
                test     Evaluate a particular sorting algorithm
                profile  Make a plot the running time of several algorithms
                ''')
        parser.add_argument('command', help='Subcommand to run')
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
            parser.print_help()
            exit(1)
        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()

    def test(self):
        choices = list(self.available_methods.keys())
        parser = argparse.ArgumentParser(
            description='Evaluate a particular sorting algorithm')
        parser.add_argument('-m', '--method', default=random.choice(choices),
            choices=choices)
        parser.add_argument('-l', '--length', type=int, default=10)
        # now that we're inside a subcommand, ignore the first
        # TWO argvs, ie the command and the subcommand
        args = parser.parse_args(sys.argv[2:])

        list_ = list(range(args.length))
        random.shuffle(list_)
        print("Testing {}".format(args.method))
        print("Input: {}".format(list_))

        sort_fn = self.available_methods[args.method]
        list_, elapsed_time = self.timeit(sort_fn, list_)
        print("Output: {}".format(list_))
        is_ok = list_ == list(range(args.length))
        print("Elapesed time: {}, Is good?: {}".format(elapsed_time, is_ok))

    def profile(self):
        
        choices = list(self.available_methods.keys())
        parser = argparse.ArgumentParser(
            description='Print the running time of several algorithms at different input sizes')
        parser.add_argument('-m', '--methods', nargs='+',
            choices=choices)
        parser.add_argument('-l', '--max-length', type=int, default=10)
        parser.add_argument('-s', '--step', type=int, default=2)
        parser.add_argument('-e', '--exponential-mode', action='store_true')
        args = parser.parse_args(sys.argv[2:])

        sort_functions = tuple(self.available_methods.items())
        if args.methods:
            sort_functions = tuple((k, fn) for k, fn in sort_functions
                if k in args.methods)

        used_names = ['Input length'] + [n for n, _ in sort_functions]
        print(used_names)
        width = max(len(str(args.max_length)), len('Input length'))
        line = "{:>{width}}" + "|{:>20}"*len(sort_functions)
        print(line.format(*used_names, width=width))
        line = "{:>{width}}" + "|{:<20.15}"*len(sort_functions)
        if args.exponential_mode:
            def help(step, max_length):
                val = step
                while val <= max_length:
                    yield val
                    val = val * step
            iterator = help(args.step, args.max_length)    
        else:
            iterator = range(args.step, args.max_length + args.step, args.step)
            
        for length in iterator:
            list_ = list(range(length))
            reference = list(range(length))
            random.shuffle(list_)
            line_results = [length]
            for name, fn in sort_functions:
                out, elapsed_time = self.timeit(fn, list_)
                if out != reference:
                    msg = "YOUR ALGORITHM {} SUCKS FOR LIST OF LENGTH {}"
                    print(msg.format(name, length))
                    sys.exit()
                line_results.append((elapsed_time))
            print(line.format(*line_results, width=width))


    @staticmethod
    def timeit(fn, *args, **kwargs):
        t0 = time.time()
        out = fn(*args, **kwargs)
        t1 = time.time()    
        return out, t1 - t0


if __name__ == "__main__":
    Tester({'bubble': bubble_sort, 'merge': merge_sort,
        'cocktail': cocktail_sort})