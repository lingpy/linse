import re
import pathlib
import unicodedata

from clldutils.misc import lazyproperty

__all__ = ['VOWELS', 'TONES', 'DIACRITICS', 'SEMI_DIACRITICS', 'STRESS', 'MODELS', 'Model']

STRESS = "ˈˌ'"
VOWELS = 'ṍεaeiouyáãæíõøúĩıœũūǒǝȇȗɐɑɒɔɘəɚɛɜɞɤɨɪɯɵɶɷɿʅʉʊʌʏᴀᴇᴜẽỹṳ'
TONES = '¹²³⁴⁵⁶⁷⁸⁹⁰₁₂₃₄₅₆₇₈₉₀0123456789˥˦˧˨˩˪˫-꜈-꜉-꜊-꜋-꜌-꜍-꜎-꜏-꜐-꜑-꜒-꜓-꜔-꜕-꜖-ꜗ-ꜘ-ꜙ-ꜚ-꜀-꜁-꜂-꜃-꜄-꜅-꜆-꜇'
DIACRITICS = frozenset({
    ' ', '!', ':', '|', '¯', 'ʰ', 'ʱ', 'ʲ', 'ʳ', 'ʴ', 'ʵ', 'ʶ', 'ʷ', 'ʸ', 'ʹ', 'ʺ', 'ʻ', 'ʼ', 'ʽ',
    'ʾ', 'ʿ', 'ˀ', 'ˀ', 'ˁ', '˂', '˃', '˄', '˅', 'ˆ', 'ˈ', 'ˉ', 'ˊ', 'ˋ', 'ˌ', 'ˍ', 'ˎ', 'ˏ', 'ː',
    'ˑ', '˒', '˓', '˔', '˕', '˖', '˗', '˞', '˟', 'ˠ', 'ˡ', 'ˢ', 'ˣ', 'ˤ', 'ˬ', '˭', 'ˮ', '˯', '˰',
    '˱', '˲', '˳', '˴', '˵', '˶', '˷', '˸', '˹', '˺', '˻', '˼', '˽', '˾', '˿', '̀', '̀', '́', '́', '́', '̂',
    '̃', '̄', '̅', '̆', '̇', '̈', '̈', '̉', '̊', '̋', '̌', '̍', '̎', '̏', '̐', '̑', '̒', '̓', '̓', '̔', '̕', '̖', '̗',
    '̘', '̙', '̚', '̛', '̜', '̝', '̞', '̟', '̠', '̡', '̢', '̣', '̤', '̥', '̦', '̧', '̨', '̩', '̪',
    '̫', '̬', '̭', '̮', '̯', '̰', '̱', '̲', '̲', '̳', '̴', '̵', '̶', '̷', '̸', '̹', '̺', '̻', '̼',
    '̽', '̾', '̿', '͂', 'ͅ', '͆', '͇', '͈', '͉', '͊', '͋', '͌', '͍', '͎', '͏', '͐', '͑', '͒', '͓', '͔', '͕', '͖', '͗', '͘', '͙', '͚',
    '͛', '͝', '͞', '͟', '͠', '͢', 'ͣ', 'ͤ', 'ͥ', 'ͦ', 'ͧ', 'ͨ', 'ͩ', 'ͪ', 'ͫ', 'ͬ', 'ͭ', 'ͮ', 'ͯ', '҃', '҄', '҅', '҆', '҇', '҈', '҉',
    'ՙ', 'ٖ', 'ٰ', 'ܑ', '߫', '߬', '߭', '߮', '߯', '߰', '߱', '߲', '߳', 'ᴬ', 'ᴭ', 'ᴮ', 'ᴯ', 'ᴰ', 'ᴱ', 'ᴲ', 'ᴳ', 'ᴴ',
    'ᴵ', 'ᴶ', 'ᴷ', 'ᴸ', 'ᴹ', 'ᴺ', 'ᴻ', 'ᴼ', 'ᴽ', 'ᴾ', 'ᴿ', 'ᵀ', 'ᵁ', 'ᵂ', 'ᵃ', 'ᵄ', 'ᵅ', 'ᵆ', 'ᵇ',
    'ᵈ', 'ᵉ', 'ᵊ', 'ᵋ', 'ᵌ', 'ᵍ', 'ᵎ', 'ᵏ', 'ᵐ', 'ᵑ', 'ᵒ', 'ᵓ', 'ᵔ', 'ᵕ', 'ᵖ', 'ᵗ', 'ᵘ', 'ᵙ', 'ᵚ',
    'ᵛ', 'ᵜ', 'ᵝ', 'ᵞ', 'ᵟ', 'ᵠ', 'ᵡ', 'ᵢ', 'ᵣ', 'ᵤ', 'ᵥ', 'ᵦ', 'ᵧ', 'ᵨ', 'ᵩ', 'ᵪ', 'ᵸ', 'ᶛ', 'ᶜ', 'ᶝ',
    'ᶞ', 'ᶟ', 'ᶠ', 'ᶡ', 'ᶢ', 'ᶣ', 'ᶤ', 'ᶥ', 'ᶦ', 'ᶧ', 'ᶨ', 'ᶩ', 'ᶪ', 'ᶫ', 'ᶬ', 'ᶭ', 'ᶮ', 'ᶯ', 'ᶰ',
    'ᶱ', 'ᶲ', 'ᶳ', 'ᶴ', 'ᶵ', 'ᶶ', 'ᶷ', 'ᶸ', 'ᶹ', 'ᶺ', 'ᶻ', 'ᶼ', 'ᶽ', 'ᶾ', 'ᶿ', '᷀', '᷁', '᷂', '᷃', '᷄', '᷅',
    '᷆', '᷇', '᷈', '᷉', '᷊', '᷋', '᷌', '᷍', '᷎', '᷏', 'ᷓ', 'ᷔ', 'ᷕ', 'ᷖ', 'ᷗ', 'ᷘ', 'ᷙ', 'ᷚ', 'ᷛ', 'ᷜ', 'ᷝ', 'ᷞ', 'ᷟ', 'ᷠ', 'ᷡ', 'ᷢ', 'ᷣ',
    'ᷤ', 'ᷥ', 'ᷦ', '᷼', '᷽', '᷾', '᷿', 'ⁱ', '⁺', '⁻', '⁼', '⁽', '⁾', 'ⁿ', '₊', '₋', '₌', '₍', '₎', 'ₐ', 'ₑ',
    'ₒ', 'ₓ', 'ₔ', 'ₕ', 'ₖ', 'ₗ', 'ₘ', 'ₙ', 'ₚ', 'ₛ', 'ₜ', '⃐', '⃑', '⃒', '⃓', '⃔', '⃕', '⃖', '⃗', '⃘', '⃙', '⃚',
    '⃛', '⃜', '⃥', '⃦', '⃧', '⃨', '⃩', '⃪', '⃫', '⃬', '⃭', '⃮', '⃯', '⃰', '→', '⇒', '⨧', 'ⱼ', 'ⱽ', 'ⵯ', 'ⷠ', 'ⷡ', 'ⷢ',
    'ⷣ', 'ⷤ', 'ⷥ', 'ⷦ', 'ⷧ', 'ⷨ', 'ⷩ', 'ⷪ', 'ⷫ', 'ⷬ', 'ⷭ', 'ⷮ', 'ⷯ', 'ⷰ', 'ⷱ', 'ⷲ', 'ⷳ', 'ⷴ', 'ⷵ', 'ⷶ', 'ⷷ', 'ⷸ', 'ⷹ', 'ⷺ', 'ⷻ', 'ⷼ', 'ⷽ',
    'ⷾ', 'ⷿ', '゙', '゚', '꙯', '꙼', '꙽', 'ꚜ', 'ꚝ', 'ꜛ', 'ꜜ', 'ꜝ', 'ꜞ', 'ꜟ', 'ꞈ', '꞉', '꞊', '꣠', '꣡', '꣢', '꣣', '꣤',
    '꣥', '꣦', '꣧', '꣨', '꣩', '꣪', '꣫', '꣬', '꣭', '꣮', '꣯', '꣰', '꣱', 'ꩰ', 'ꭜ', 'ꭞ', '\uf1af', '︠', '︡', '︢', '︣', '︤',
    '︥', '︦'})
SEMI_DIACRITICS = 'hsʃ̢ɕʂʐʑʒw'


class Model(object):
    """
    Class for the handling of sound-class models.

    Parameters
    ----------

    model : { 'sca', 'dolgo', 'asjp', 'art', '_color' }
        A string indicating the name of the model which shall be loaded.
        Select between:

        * 'sca' - the SCA sound-class model (see :evobib:`List2012a`),
        * 'dolgo' - the DOLGO sound-class model (see:
          :evobib:`Dolgopolsky1986'),
        * 'asjp' - the ASJP sound-class model (see
          :evobib:`Brown2008` and :evobib:`Brown2011`),
        * 'art' - the sound-class model which is used for the calculation of
          sonority profiles and prosodic strings (see :evobib:`List2012`), and
        * '_color' - the sound-class model which is used for the coloring of
          sound-tokens when creating html-output.

    Notes
    -----
    Models are loaded from binary files which can be found in the
    :file:`data/models/` folder of the LingPy package. A model has two
    essential attributes:

    * :py:attr:`converter` -- a dictionary with IPA-tokens as keys and
      sound-class characters as values, and
    * :py:attr:`scorer` -- a scoring dictionary with tuples of sound-class
      characters as keys and scores (integers or floats) as values.

    Attributes
    ----------
    converter : dict
        A dictionary with IPA tokens as keys and sound-class characters as
        values.

    scorer : dict
        A scoring dictionary with tuples of sound-class characters as keys and
        similarity scores as values.

    info : dict
        A dictionary storing the key-value pairs defined in the ``INFO``.

    name : str
        The name of the model which is identical with the name of the folder
        from wich the model is loaded.

    Examples
    --------
    When loading LingPy, the models ``sca``, ``asjp``, ``dolgo``, and ``art``
    are automatically loaded, and they are accessible via the
    :py:func:`~lingpy.settings.rc` function for
    global settings:

    >>> from lingpy import *
    >>> rc('asjp')
    <sca-model "asjp">

    Define variables for the standard models for convenience:

    >>> asjp = rc('asjp')
    >>> sca = rc('sca')
    >>> dolgo = rc('dolgo')
    >>> art = rc('art')

    Check how the letter ``a`` is converted in the various models:

    >>> for m in [asjp,sca,dolgo,art]:
    ...     print('{0} > {1} ({2})'.format('a',m.converter['a'],m.name))
    ...
    a > a (asjp)
    a > A (sca)
    a > V (dolgo)
    a > 7 (art)

    Retrieve basic information of a given model:

    >>> print(sca)
    Model:    sca
    Info:     Extended sound class model based on Dolgopolsky (1986)
    Source:   List (2012)
    Compiler: Johann-Mattis List
    Date:     2012-03
    """
    def __init__(self, d):
        self.dir = pathlib.Path(d)
        assert self.dir.exists() and self.dir.is_dir()
        self.name = self.dir.name

    @lazyproperty
    def info(self):
        res = {}
        fname = self.dir / 'INFO'
        if fname.exists():
            text = fname.read_text(encoding='utf-8-sig')
            for line in ['description', 'compiler', 'source', 'date', 'vowels', 'tones']:
                res[line] = ''
                for m in re.findall('@' + line + ': (.*)', text):
                    res[line] = m
                    break
        return res

    @lazyproperty
    def vowels(self):
        return self.info.get('vowels')

    @lazyproperty
    def tones(self):
        return self.info.get('tones')

    @lazyproperty
    def converter(self):
        """
        Function imports individually defined sound classes from a text file and
        creates a replacement dictionary from these sound classes.
        """
        sc_repl_dict = {}
        for line in self.dir.joinpath('converter').open(encoding='utf-8-sig'):
            key, v = unicodedata.normalize('NFC', line.strip()).split(' : ')
            for value in v.split(','):
                value = value.strip()
                if value in sc_repl_dict and sc_repl_dict[value] != key:
                    raise ValueError("Values {0} in file {1} are multiply defined!".format(
                        value, self.dir / 'converter'))
                sc_repl_dict[value] = key
        return sc_repl_dict

    def __str__(self):
        out = 'Model:    {0}\nInfo:     {1}\nSource:   {2}\nCompiler: {3}\nDate:     {4}'
        return out.format(
            self.name,
            self.info['description'],
            self.info['source'],
            self.info['compiler'],
            self.info['date']
        )

    def __repr__(self):
        return '<sca-model "' + self.name + '">'

    def __getitem__(self, x):
        return self.converter[x]

    def __contains__(self, x):
        return x in self.converter

    def __eq__(self, x):
        """
        Compare a sound-class model with another model.
        """
        return self.__repr__() == x.__repr__()


MODELS = {
    d.name: Model(d)
    for d in pathlib.Path(__file__).parent.joinpath('models').iterdir()
    if d.joinpath('converter').exists()}
