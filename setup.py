from setuptools import find_packages, setup

setup(
  name='AlgoTrading_Colab',
  version="0.0.1",
  packages=find_packages(),
  entrypoints={
    'console_scripts': [
      'AlgoTrading_Colab=algotradingcolab.main:main',
    ],
  },
)