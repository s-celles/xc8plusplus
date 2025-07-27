extern "C" int cpp_func() { class Test { public: int get() { return 42; } }; Test t; return t.get(); }
