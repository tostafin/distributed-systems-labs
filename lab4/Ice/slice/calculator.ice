
#ifndef CALC_ICE
#define CALC_ICE

module Demo
{
  enum operation { MIN, MAX, AVG };

  sequence<double> FloatNumbers;
  
  exception NoInput {};

  struct A
  {
    short a;
    long b;
    float c;
    string d;
  }

  interface Calc
  {
    long add(int a, int b);
    long subtract(int a, int b);
    void op(A a1, short b1); //za?�?my, ?e to te? jest operacja arytmetyczna ;)
    double avg(FloatNumbers numbers);
  };
};

#endif
