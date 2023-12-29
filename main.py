import numpy as np
from math import ceil

class MembershipFunction:
    def __init__(self, shape, params):
        self.shape = shape
        self.params = params

    def get_degree_of_membership(self, value):
        if self.shape == 'TRI':
            a, b, c = self.params
            if value <= a:
                return 0
            elif value <= b:
                return (value - a) / (b - a)
            elif value <= c:
                return (c - value) / (c - b)
            else:
                return 0
        elif self.shape == 'TRAP':
            a, b, c, d = self.params
            if value <= a:
                return 0
            elif value <= b:
                return (value - a) / (b - a)
            elif value <= c:
                return 1
            elif value <= d:
                return (d - value) / (d - c)
            else:
                return 0



class FuzzyVariable:
    def __init__(self, name, v_type, ranges):
        self.name = name
        self.type = v_type
        self.ranges = ranges
        self.fuzzy_sets = {}

    def add_fuzzy_set(self, name, f_type, membership_function_params):
        membership_function = MembershipFunction(f_type, membership_function_params)
        fuzzy_set = FuzzySet(name, f_type, membership_function)
        self.fuzzy_sets[name] = fuzzy_set

    def fuzzify(self, crisp_values):
        fuzzified_values = {}

        for fuzzy_set in self.fuzzy_sets.values():
            crisp_value = crisp_values.get(self.name, 0.0)
            degree = fuzzy_set.membership_function.get_degree_of_membership(crisp_value)
            fuzzified_values[fuzzy_set.name] = degree

        return fuzzified_values

class FuzzySet:
    def __init__(self, name, f_type, membership_function):
        self.name = name
        self.type = f_type
        self.membership_function = membership_function
        self.centroid = None  # Add centroid attribute

class FuzzyRule:
    def __init__(self, var1, set1, operator, var2, set2, output_var, output_set):
        self.var1 = var1
        self.set1 = set1
        self.operator = operator
        self.var2 = var2
        self.set2 = set2
        self.output_var = output_var
        self.output_set = output_set


class FuzzyLogicToolbox:
    def __init__(self):
        self.variables = []
        self.rules = []

    def add_variable(self, name, v_type, ranges):
        self.variables.append(FuzzyVariable(name, v_type, ranges))

    def add_fuzzy_set(self, variable_name, set_name, set_type, membership_function_params):
        variable = next((var for var in self.variables if var.name == variable_name), None)
        if variable:
            variable.add_fuzzy_set(set_name, set_type, membership_function_params)
        else:
            print(f"Variable '{variable_name}' not found.")

    def add_rule(self, rule_input):
        rule_parts = rule_input.split()
        if len(rule_parts) == 7:
            var1, set1, operator, var2, set2, output_var, output_set = rule_parts
            self.rules.append(FuzzyRule(var1, set1, operator, var2, set2, output_var, output_set))
            print(f'Rule added: If {var1} {set1} {operator} {var2} {set2} => {output_var} {output_set}')
        else:
            print("Invalid rule format. Please use: IN_variable set operator IN_variable set => OUT_variable set")

    def fuzzify_variables(self, crisp_values):
        fuzzified_values = {}
        for variable in self.variables:
            fuzzified_values[variable.name] = variable.fuzzify(crisp_values)
        return fuzzified_values

    def evaluate_rules(self, rules, fuzzified_values, output_degrees):
        degrees_array = []

        for rule in rules:
            var1, set1, operator, var2, set2, output_var, output_set = (
                rule.var1, rule.set1, rule.operator, rule.var2, rule.set2, rule.output_var, rule.output_set)

            # Perform fuzzy operations based on the operator
            if operator == 'or':
                degree = np.max([fuzzified_values[var1][set1], fuzzified_values[var2][set2]])
            elif operator == 'and':
                degree = np.min([fuzzified_values[var1][set1], fuzzified_values[var2][set2]])
            elif operator == 'and_not':
                degree = np.min([0, 1 - fuzzified_values[var1][set1]])
            else:
                print('Invalid operator. Please use "or", "and", or "and_not".')
                return []

            # Accumulate the degree for the same output set
            if output_set in output_degrees:
                degree = output_degrees[output_set] = max(output_degrees[output_set], degree)
            else:
                output_degrees[output_set] = degree

            # Append the set name along with the degree (rounded to 1 decimal place)
            degrees_array.append((output_set, round(degree, 1)))

        return degrees_array

    def calculate_centroid_value(self, membership_function, degree):
        shape = membership_function.shape
        params = membership_function.params

        if shape == 'TRI':
            a, b, c = params
            centroid = (a + b + c) / 3
        elif shape == 'TRAP':
            a, b, c, d = params
            centroid = (a + b + c + d) / 4
        else:
            centroid = None
        print("centroid",centroid)
        return centroid

    def calculate_and_print_centroid(self, crisp_values):
        # Fuzzification step
        fuzzified_values = self.fuzzify_variables(crisp_values)
        print("fuzzified_values", fuzzified_values)
        # Extract dynamic output set names
        output_degrees = {}
        total_degrees = 0
        # Evaluate all rules and get degrees array
        degs_arr = self.evaluate_rules(self.rules, fuzzified_values, output_degrees)
        # Remove duplication
        degs_arr = list(set(degs_arr))

        print("degs_arr", degs_arr)

        centroids = {}
        weighted_sum = 0
        variable = next((var for var in self.variables if var.type == 'OUT'), None)

        for set_name, degree in degs_arr:
            total_degrees += degree

            # Get the centroid value for the current set_name
            if variable:
                membership_function = variable.fuzzy_sets[set_name].membership_function
                centroid_value = self.calculate_centroid_value(membership_function, degree)
                centroids[set_name] = centroid_value

                # Sum the product of degree and centroid for each set
                weighted_sum += degree * centroid_value
        print("weighted_sum", weighted_sum)

        # Calculate the overall centroid by dividing the weighted sum by the total degrees
        if total_degrees != 0:
            overall_centroid = weighted_sum / total_degrees

            print("The Predicted", variable.name, "is", round(overall_centroid, 1))
        else:
            print("Total degrees is zero, unable to calculate overall centroid.")

if __name__ == '__main__':
    fuzzy_logic_toolbox_instance = FuzzyLogicToolbox()

    print("===================")
    print("Fuzzy Logic Toolbox")
    print("===================")

    while True:
        print("1 - Create a new fuzzy system")
        print("2 - Quit")

        choice = input()
        if choice == '1':
            print("Enter the system’s name and a brief description:")
            system_name = input()
            system_description = input()
            print("Main Menu:")
            print("==========")

            while True:
                print("1 - Add variables.")
                print("2 - Add fuzzy sets to an existing variable.")
                print("3 - Add rules.")
                print("4 - Run the simulation on crisp values.")
                print("x - Exit to Main Menu.")

                sub_choice = input()

                if sub_choice == '1':
                    print("Enter the variable’s name, type (IN/OUT), and range ([lower, upper]):")
                    print("(Press x to finish)")

                    while True:
                        variable_input = input()
                        if variable_input.lower() == 'x':
                            break
                        else:
                            name, v_type, ranges = variable_input.split()
                            ranges = list(map(int, ranges[1:-1].split(',')))
                            fuzzy_logic_toolbox_instance.add_variable(name, v_type, ranges)

                elif sub_choice == '2':
                    print("Enter the variable’s name:")
                    variable_name = input()
                    print("Enter the fuzzy set name, type (TRI/TRAP), and values:")
                    print("(Press x to finish)")

                    while True:
                        fuzzy_set_input = input()
                        if fuzzy_set_input.lower() == 'x':
                            break
                        else:
                            set_name, set_type, *values = fuzzy_set_input.split()
                            values = list(map(float, values))
                            fuzzy_logic_toolbox_instance.add_fuzzy_set(variable_name, set_name, set_type, values)

                elif sub_choice == '3':
                    print("Enter the rules in this format:")
                    print("(Press x to finish)")
                    print("IN_variable set operator IN_variable set => OUT_variable set")

                    while True:
                        rule_input = input()
                        if rule_input.lower() == 'x':
                            break
                        else:
                            fuzzy_logic_toolbox_instance.add_rule(rule_input)


                elif sub_choice == '4':

                    print("Enter the crisp values:")

                    crisp_values = {}

                    for variable in fuzzy_logic_toolbox_instance.variables:

                        if variable.type != 'OUT':  # Skip output variables

                            value = float(input(f"{variable.name}: "))

                            crisp_values[variable.name] = value

                    print("Running the simulation…")

                    fuzzy_logic_toolbox_instance.calculate_and_print_centroid(crisp_values)

                elif sub_choice.lower() == 'x':
                    break

        elif choice == '2':
            break
