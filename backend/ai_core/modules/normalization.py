import os

class NormalizationModule:
    def __init__(self, max_dictionary_edit_distance=2, prefix_length=7):
        self.mock_mode = False
        try:
            import pkg_resources
            from symspellpy import SymSpell, Verbosity
            
            # Create SymSpell object
            self.sym_spell = SymSpell(max_dictionary_edit_distance, prefix_length)
            
            # Load default dictionary
            dictionary_path = pkg_resources.resource_filename(
                "symspellpy", "frequency_dictionary_en_82_765.txt"
            )
            bigram_path = pkg_resources.resource_filename(
                "symspellpy", "frequency_bigramdictionary_en_243_342.txt"
            )
            
            if not self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1):
                print("Warning: Dictionary file not found")
            if not self.sym_spell.load_bigram_dictionary(bigram_path, term_index=0, count_index=2):
                print("Warning: Bigram dictionary file not found")
                
            print("SymSpell loaded for normalization.")
        except ImportError as e:
            print(f"WARNING: SymSpell dependencies missing ({e}). Using Mock Mode.")
            self.mock_mode = True

    def normalize(self, text):
        """
        Corrects spelling errors in the input text using SymSpell compound lookup.
        """
        if self.mock_mode:
            return text

        suggestions = self.sym_spell.lookup_compound(
            text, max_edit_distance=2
        )
        
        # return the best suggestion
        if suggestions:
            return suggestions[0].term
        return text

if __name__ == "__main__":
    norm = NormalizationModule()
    sample = "play spotifi song"
    corrected = norm.normalize(sample)
    print(f"Original: {sample} -> Corrected: {corrected}")
