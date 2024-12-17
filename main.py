import random
import tkinter as tk
from tkinter import messagebox, filedialog
from itertools import product
from pyformlang.regular_expression import Regex
from pyformlang.finite_automaton import Symbol, DeterministicFiniteAutomaton, State
import pydot
from io import StringIO

# Define the functions from the original code
def rename_states(dfa):
    state_mapping = {state: State(chr(65 + idx)) for idx, state in enumerate(dfa.states)}
    renamed_dfa = dfa.__class__()

    renamed_dfa.add_start_state(state_mapping[dfa.start_state])

    for final_state in dfa.final_states:
        renamed_dfa.add_final_state(state_mapping[final_state])

    for state in dfa.states:
        for symbol in dfa.symbols:
            transitions = dfa.to_dict()
            if state in transitions and symbol in transitions[state]:
                next_state = transitions[state][symbol]
                renamed_dfa.add_transition(state_mapping[state], symbol, state_mapping[next_state])

    return renamed_dfa

def add_final_state_self_loops(dfa):
    transitions = dfa.to_dict()

    for final_state in dfa.final_states:
        for state, transition_dict in transitions.items():
            for symbol, next_state in transition_dict.items():
                if next_state == final_state:
                    dfa.add_transition(final_state, symbol, final_state)

    return dfa

def user_regex_to_dfa(regex_string):
    try:
        dfa = Regex(regex_string).to_epsilon_nfa().to_deterministic().minimize()
        renamed_dfa = rename_states(dfa)
        renamed_dfa = add_final_state_self_loops(renamed_dfa)
        return renamed_dfa
    except Exception as e:
        return None

def generate_random_string(dfa, max_length):
    transitions = dfa.to_dict()
    for _ in range(100):
        current_state = dfa.start_state
        random_string = ""
        for _ in range(max_length):
            if current_state not in transitions:
                break
            possible_transitions = {
                symbol: transitions[current_state][symbol]
                for symbol in transitions[current_state]
            }

            if not possible_transitions:
                break

            symbol = random.choice(list(possible_transitions.keys()))
            current_state = possible_transitions[symbol]
            random_string += str(symbol)

            if current_state in dfa.final_states:
                return random_string
    return None

def enumerate_strings(dfa, max_length):
    valid_strings = []
    alphabet = list(dfa.symbols)

    for length in range(1, max_length + 1):
        for sequence in product(alphabet, repeat=length):
            if dfa.accepts(sequence):
                valid_strings.append("".join(map(str, sequence)))

    return valid_strings



def visualize_dfa(dfa):
    graph = pydot.Dot(graph_type="digraph", rankdir="LR")

    # Add nodes
    for state in dfa.states:
        state_str = str(state)  # Ensure the state is converted to string
        if state == dfa.start_state:
            graph.add_node(pydot.Node(state_str, shape="circle", style="filled", fillcolor="lightgreen"))
        elif state in dfa.final_states:
            graph.add_node(pydot.Node(state_str, shape="doublecircle", style="filled", fillcolor="lightblue"))
        else:
            graph.add_node(pydot.Node(state_str, shape="circle", style="filled", fillcolor="gray"))

    # Add edges
    for state, transitions in dfa.to_dict().items():
        state_str = str(state)  # Convert state to string for edges
        for symbol, next_state in transitions.items():
            next_state_str = str(next_state)  # Convert next state to string for edges
            graph.add_edge(pydot.Edge(state_str, next_state_str, label=str(symbol)))

    # Write the graph to a PNG image
    img_path = "dfa_graph.png"
    graph.write_png(img_path)  # Use write_png to save the image

    return graph  # Return the graph object instead of a string


class DFAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DFA Generator Tool")
        
        self.dfa = None
        self.max_length = 5
        self.num_strings = 5
        self.max_enum_length = 5

        # Create the main layout
        self.create_widgets()

    def create_widgets(self):
        # Radio buttons to choose between generating from regex or manually creating automaton
        self.option_var = tk.StringVar(value="Generate from Regex")
        tk.Radiobutton(self.root, text="Generate from Regex", variable=self.option_var, value="Generate from Regex", command=self.update_ui).pack()
        tk.Radiobutton(self.root, text="Make Own Automaton", variable=self.option_var, value="Make Own Automaton", command=self.update_ui).pack()

        # Regular expression input for generating DFA
        self.regex_label = tk.Label(self.root, text="Enter Regular Expression:")
        self.regex_input = tk.Entry(self.root, width=40)
        self.regex_label.pack()
        self.regex_input.pack()

        # Start button for generating DFA from regex
        self.generate_button = tk.Button(self.root, text="Generate DFA", command=self.generate_dfa)
        self.generate_button.pack()

        # Option for generating random strings
        self.num_strings_label = tk.Label(self.root, text="Number of random strings to generate:")
        self.num_strings_input = tk.Entry(self.root)
        self.num_strings_input.insert(0, str(self.num_strings))
        self.num_strings_label.pack()
        self.num_strings_input.pack()

        self.max_length_label = tk.Label(self.root, text="Maximum string length:")
        self.max_length_input = tk.Entry(self.root)
        self.max_length_input.insert(0, str(self.max_length))
        self.max_length_label.pack()
        self.max_length_input.pack()

        self.generate_random_button = tk.Button(self.root, text="Generate Random Strings", command=self.generate_random_strings)
        self.generate_random_button.pack()

        # Option for enumerating valid strings
        self.max_enum_length_label = tk.Label(self.root, text="Maximum enumeration length:")
        self.max_enum_length_input = tk.Entry(self.root)
        self.max_enum_length_input.insert(0, str(self.max_enum_length))
        self.max_enum_length_label.pack()
        self.max_enum_length_input.pack()

        self.enumerate_button = tk.Button(self.root, text="Enumerate Valid Strings", command=self.enumerate_valid_strings)
        self.enumerate_button.pack()

        self.output_label = tk.Label(self.root, text="")
        self.output_label.pack()

    def update_ui(self):
        if self.option_var.get() == "Generate from Regex":
            self.regex_label.pack()
            self.regex_input.pack()
            self.generate_button.pack()
        else:
            self.regex_label.pack_forget()
            self.regex_input.pack_forget()
            self.generate_button.pack_forget()

    def generate_dfa(self):
        regex_string = self.regex_input.get()
        if regex_string:
            self.dfa = user_regex_to_dfa(regex_string)
            if self.dfa:
                self.output_label.config(text="DFA generated successfully!")
                self.visualize_dfa(self.dfa)  # Pass the dfa object here
            else:
                messagebox.showerror("Error", "Failed to generate DFA.")
        else:
            messagebox.showerror("Input Error", "Please enter a regular expression.")

    def generate_random_strings(self):
        if self.dfa:
            self.num_strings = int(self.num_strings_input.get())
            self.max_length = int(self.max_length_input.get())
            strings = []
            for _ in range(self.num_strings):
                rand_string = generate_random_string(self.dfa, self.max_length)
                if rand_string:
                    strings.append(rand_string)
                else:
                    strings.append("Failed to generate a valid string.")
            self.output_label.config(text="\n".join(strings))
        else:
            messagebox.showerror("Error", "Please generate a DFA first.")

    def enumerate_valid_strings(self):
        if self.dfa:
            self.max_enum_length = int(self.max_enum_length_input.get())
            valid_strings = enumerate_strings(self.dfa, self.max_enum_length)
            self.output_label.config(text=f"Total strings found: {len(valid_strings)}\n" + "\n".join(valid_strings))
        else:
            messagebox.showerror("Error", "Please generate a DFA first.")

    def visualize_dfa(self, dfa):  # Update method to accept dfa parameter
        graph = pydot.Dot(graph_type="digraph", rankdir="LR")

        # Add nodes
        for state in dfa.states:
            state_str = str(state)  # Ensure the state is converted to string
            if state == dfa.start_state:
                graph.add_node(pydot.Node(state_str, shape="circle", style="filled", fillcolor="lightgreen"))
            elif state in dfa.final_states:
                graph.add_node(pydot.Node(state_str, shape="doublecircle", style="filled", fillcolor="lightblue"))
            else:
                graph.add_node(pydot.Node(state_str, shape="circle", style="filled", fillcolor="gray"))

        # Add edges
        for state, transitions in dfa.to_dict().items():
            state_str = str(state)  # Convert state to string for edges
            for symbol, next_state in transitions.items():
                next_state_str = str(next_state)  # Convert next state to string for edges
                graph.add_edge(pydot.Edge(state_str, next_state_str, label=str(symbol)))

        # Write the graph to a PNG image
        img_path = "dfa_graph.png"
        graph.write_png(img_path)  # Use write_png to save the image

        return graph  # Return the graph object instead of a string

def main():
    root = tk.Tk()
    app = DFAApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()