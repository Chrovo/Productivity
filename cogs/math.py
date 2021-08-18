import operator
import re
from io import BytesIO

import discord
from discord.ext import commands
from matplotlib import pyplot as plt


class Math(commands.Cog):
    """Math commands."""

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        self.emoji = "🔢" # create custom emojis later I guess.

    def save_plt(self, _plt, name:str) -> discord.File:
        _bytes = BytesIO()
        _plt.savefig(_bytes)
        _plt.close()
        img = discord.File(_bytes, name)
        _bytes.seek(0)
        return img      

    @commands.command(description="Graph a linear function!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def linear(self, ctx, slope:float, y_intercept:float):
        x = list(range(-10, 11))
        y = [(slope*x_val)+y_intercept for x_val in x]

        plt.plot(x, y, linestyle='-')
        plt.grid()

        img = self.save_plt(plt, "linear.png")

        await ctx.send(file=img)

    @commands.command(description="Graph a quadratic function!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quadratic(self, ctx, a:float, b:float, c:float):
        x = list(range(-10, 11))
        y = [a*x_val**2 + b*x_val + c for x_val in x]

        plt.plot(x, y, linestyle='-')
        plt.grid()

        img = self.save_plt(plt, "quadratic.png")
        
        await ctx.send(file=img)

    @commands.command(description="Graph a exponential function")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def exponential(self, ctx, a:float, b:float):
        x = list(range(-10, 11))
        y = [a*b**x_val for x_val in x]

        plt.plot(x, y, linestyle='-')
        plt.grid()

        img = self.save_plt(plt, "exponential.png")

        await ctx.send(file=img)

    def pemdas(self, expr:str) -> list:
        """This function will return a list in the order 
        you are supposed to solve an expression, eg.) 
        the expression '1 + 2(2/3)' will return 
        [2, operator.truediv, 3, operator.mul, 2, operator.add, 1]
        which is found by PEMDAS.
        """
        results = []

        #Problem: It interprets 1 + 2 * 3 as ['2', '*', '3', '1', '+', '2'] meaning, the 2 is repeated, causing the problems to be wrong
        #fix later cus lazy atm, also this code doesnt look very nice so I will try to simplify it later

        EXPONENT_REGEX = re.compile(r"[0-9 ]+[\.]?[0-9 ]+\^[0-9 ]+[\.]?[0-9 ]+")
        MULTIPLICATION_REGEX = re.compile(r"[0-9 ]+[\.]?[0-9 ]\*[0-9 ]+[\.]?[0-9 ]+")
        DIVISION_REGEX = re.compile(r"[0-9 ]+[\.]?[0-9 ]\/[0-9 ]+[\.]?[0-9 ]+")
        ADDITION_REGEX = re.compile(r"[0-9 ]+[\.]?[0-9 ]\+[0-9 ]+[\.]?[0-9 ]+")
        SUBTRACTION_REGEX = re.compile(r"[0-9 ]+[\.]?[0-9 ]\-[0-9 ]+[\.]?[0-9 ]+")

        exponent = re.finditer(EXPONENT_REGEX, expr)
        multiplication = re.finditer(MULTIPLICATION_REGEX, expr)
        division = re.finditer(DIVISION_REGEX, expr)
        addition = re.finditer(ADDITION_REGEX, expr)
        subtraction = re.finditer(SUBTRACTION_REGEX, expr)

        all_operators = [exponent, multiplication, division, addition, subtraction]

        for operator in all_operators:
            for matchobj in operator:
                end = matchobj.end()
                start = matchobj.start()
                sliced = expr[start:end].replace(" ", "")

                for char in list(sliced):
                    results.append(char)

        return results

    @commands.command(description="Calculate an expression!", aliases=["calculate", "calculator"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def calc(self, ctx, *, expr:str):
        list_expression = self.pemdas(expr)

        OPERATORS = {
            '+':operator.add, 
            '-':operator.sub, 
            '/':operator.truediv, 
            '*':operator.mul, 
            '^':pow,
            }

        expression = []

        try:

            for char in list_expression:
                try:
                    expression.append(OPERATORS[char])
                except KeyError:
                    expression.append(float(char))

            for index, character in enumerate(expression):
                if not isinstance(character, float):

                    try:
                        answer = character(expression[index-1], expression[index+1])

                        expression.pop(index+1)
                        expression.pop(index)
                        expression.pop(index-1)

                        expression.insert(index-1, answer)
                    except IndexError:
                        continue

                else:
                    continue
            
            total = sum(expression)

            return await ctx.send(f"{expr} = {total}")

        except Exception:
            return await ctx.send("Invalid Equation!")


def setup(bot):
    bot.add_cog(Math(bot))