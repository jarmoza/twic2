import os
import sys
import yaml

# def load_src(name, fpath):
#     import os, imp
#     return imp.load_source(name, os.path.join(os.path.dirname(__file__), fpath))
# load_src("utils_malletinterpret", os.path.join("..", "utils", "utils_malletinterpret.py"))

def add_sibling_path(p_folder_name):
    full_path = os.path.abspath(os.path.join(".", "..", p_folder_name))
    if full_path not in sys.path:
        sys.path.insert(0, full_path)

add_sibling_path("utils")
from utils_malletinterpret import Utils_MalletInterpret

from twic_malletscript import TWiC_MalletScript
from twic_malletinterpret import TWiC_MalletInterpret
from twic_text import TWiC_Text

def CreateMallet(p_mallet_yaml_parameters):

    # Create a TWiC_MalletScript object
    mallet_script = TWiC_MalletScript()

    # Set up variables necessary for script run
    mallet_script.TextClass = TWiC_Text

    twic_relative_root = os.path.join("..", "..", ".." + os.sep)

    # For GatherTexts
    mallet_script.GatherTexts = TWiC_Text.GatherTexts
    mallet_script.user_source_dir = p_mallet_yaml_parameters["user_source_path"]
    if os.sep != mallet_script.user_source_dir[len(mallet_script.user_source_dir) - 1]:
        mallet_script.user_source_dir += os.sep
    mallet_script.corpus_source_dir = twic_relative_root + os.path.join("data", "input", "txt" + os.sep)

    # For RunMallet
    mallet_script.corpus_name = p_mallet_yaml_parameters["corpus_short_name"]
    mallet_script.output_dir = twic_relative_root + os.path.join("data", "output", "mallet" + os.sep)
    mallet_script.stopwords_dir = twic_relative_root + os.path.join("data", "output", "stopwords" + os.sep)
    #mallet_script.lda_dir = twic_relative_root + "lib/mallet-2.0.7/"
    mallet_script.lda_dir = twic_relative_root + os.path.join("lib", "mallet" + os.sep)
    mallet_script.script_dir = os.getcwd()
    mallet_script.num_topics = str(p_mallet_yaml_parameters["num_topics"])
    mallet_script.num_intervals = str(p_mallet_yaml_parameters["num_intervals"])
    mallet_script.text_chunk_size_words = int(p_mallet_yaml_parameters["text_chunk_size_words"])

    # For InterpretMalletOutput
    mallet_script.BuildOutputNames()
    mallet_script.corpus_title = p_mallet_yaml_parameters["corpus_full_name"]
    mallet_script.InterpretMalletOutput = TWiC_MalletInterpret.InterpretMalletOutput

    # Return the now-configured TWiC_MalletScript object
    return mallet_script


def ReadTWiCYAML():

    twic_relative_root = os.path.join("..", "..", ".." + os.sep)
    twic_config_filename = "twic_config.yaml"
    twic_config_path = os.getcwd() + os.sep + twic_relative_root

    # Make sure YAML config file exists
    if not os.path.isfile(twic_config_path + twic_config_filename):
        return None

    with open(twic_config_path + twic_config_filename, "rU") as yaml_file:
        mallet_yaml_parameters = yaml.safe_load(yaml_file)

    return mallet_yaml_parameters


def Corpus2Vis(p_args):

    # Check for proper arguments or "help" argument (p_args[0]: script name, p_args[1]: twic options)
    if len(p_args) != 2 or (len(p_args) and "--help" in p_args):
        print("Usage: python twic_corpus2vis.py [gkcmi]")
        print("Options: {0}".format("\n\tg - Gather texts from user source directory\n" +\
                                    "\tk - Keep current txt files in corpus source directory\n" +
                                    "\t\t(only used if 'g' option is also used)\n" +\
                                    "\tc - Clear recent MALLET output files\n" +\
                                    "\tm - Run MALLET\n" +\
                                    "\ti - Interpret MALLET's output\n"))
        return

    # Look for YAML configuration file
    mallet_yaml_parameters = ReadTWiCYAML()
    if None == mallet_yaml_parameters:
        print("YAML file 'twic_config.yaml' not found in TWiC's root directory.")
        print("Please see README.md or github.com/jarmoza/twic/README.md for config file setup instructions.")
        return

    print("\nTopic Words in Context (TWiC)")
    print("\tby Jonathan Armoza (github.com/jarmoza), 2017.\n")
    print("This work is licensed under the GNU General Public License, Version 3.0.")
    print("See https://www.gnu.org/licenses/gpl-3.0.en.html for details.\n")

    # Create a TWiC_MalletScript object
    mallet_script = CreateMallet(mallet_yaml_parameters)

    # Build output file names based on the YAML parameters
    mallet_script.BuildOutputNames()

    # Save the supplied TWiC parameters
    twic_options = p_args[1]

    # Options dictionary
    options_dict = { "gather_texts" : "g",
                     "keep_corpus_source" : "k",
                     "clear_oldoutput" : "c",
                     "run_mallet" : "m",
                     "interpret_output" : "i" }

    # Run parts of the corpus 2 visualization workflow
    if options_dict["gather_texts"] in twic_options:
        # Clears previous files in the corpus source directory if not directed otherwise
        if options_dict["keep_corpus_source"] not in twic_options:
            mallet_script.ClearCorpusSourceDirectory()
        mallet_script.GatherTexts(mallet_script.user_source_dir, mallet_script.corpus_source_dir, True)

    # Clear MALLET's old output files
    if options_dict["clear_oldoutput"] in twic_options:
        mallet_script.ClearOutputFiles()

    # Run MALLET
    if options_dict["run_mallet"] in twic_options:
        mallet_script.RunMallet()

    # Interpret MALLET's output into TWiC's custom JSON files for its D3 visualization
    if options_dict["interpret_output"] in twic_options:
        mallet_script.InterpretMalletOutput(mallet_script)


def main(args):

    Utils_MalletInterpret.TimeAndRun(Corpus2Vis, args)


if '__main__' == __name__:
    main(sys.argv)
