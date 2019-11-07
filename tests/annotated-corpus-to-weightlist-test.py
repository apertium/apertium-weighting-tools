import unittest
import tempfile
import subprocess
from pathlib import Path
class TestAnnotatedCorpusToWeightlist(unittest.TestCase):
	def test(self):
		temp_dir = tempfile.mkdtemp()
		temp_analysis_weightlist = Path(temp_dir, 'temp_analysis_weightlist')
		temp_tag_weightlist = Path(temp_dir, 'temp_tag_weightlist')
		temp_default_weightlist = Path(temp_dir, 'temp_default_weightlist')
		
		tagged_corpus = 'data/tagged-corpus'

		input_dict = 'data/minimal-mono.dix'
		compiled_dict = Path(temp_dir, 'temp_compiled_dict')
		weighted_dict = Path(temp_dir, 'temp_weighted_dict')

		subprocess.run(['lt-comp', 'lr', input_dict, compiled_dict])

		subprocess.run(['../annotated-corpus-to-weightlist',
						tagged_corpus,
						temp_analysis_weightlist,
						'--tag_weightlist',
						temp_tag_weightlist,
						'--default_weightlist',
						temp_default_weightlist])

		subprocess.run(['../lt-weight',
						compiled_dict,
						weighted_dict,
						temp_analysis_weightlist,
						temp_tag_weightlist,
						temp_default_weightlist])
		input_file = 'data/input'
		output_file = Path(temp_dir, 'output')

		subprocess.run(['lt-proc', weighted_dict, input_file, output_file])
		# TODO: ASSERT The outputs
		lines = ['^abc/ab<n><def>/ab<n><ind>$',
				 '^def/de<n><def>/de<vblex>$']

		with open(output_file, 'r') as f:
			for out, correct_out in zip(f.readlines(), lines):
				out = out.strip()
				self.assertEqual(out, correct_out)

if __name__ == '__main__':
	unittest.main()