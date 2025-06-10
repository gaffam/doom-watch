from setuptools import setup

setup(
    name='doom-watch',
    version='0.1',
    py_modules=['doom_watch', 'streamlit_app', 'anomaly', 'momentum',
                'sentiment', 'rule_miner', 'market_watch', 'alerts',
                'llm_scenarios', 'politika_scenarios', 'doom_watch_modules',
                'bridge', 'config'],
    install_requires=[
        'streamlit',
        'pandas',
        'numpy',
        'matplotlib',
        'requests',
        'feedparser',
        'transformers',
        'torch',
        'scikit-learn'
    ],
    entry_points={'console_scripts': ['doom-watch=doom_watch:main']}
)
