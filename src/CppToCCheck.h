//===--- CppToCCheck.h - clang-tidy -----------------------------------===//
//
// XC8 C++ to C transformation using clang-tidy framework
// This demonstrates the CORRECT approach - declarative AST matching!
//
//===----------------------------------------------------------------------===//

#ifndef LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_XC8_CPPTOCCHECK_H
#define LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_XC8_CPPTOCCHECK_H

#include "clang-tidy/ClangTidy.h"
#include "clang-tidy/ClangTidyCheck.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"

namespace clang {
namespace tidy {
namespace xc8 {

/// XC8 C++ to C transpiler using clang-tidy framework
///
/// This check transforms C++ classes and methods to C equivalents:
/// - Classes become typedef structs
/// - Methods become functions taking struct pointer as first parameter
/// - Constructors become init functions  
/// - Destructors become cleanup functions
/// - Member calls become function calls
///
/// This is the XC8 approach using:
/// - AST Matchers (declarative pattern matching)
/// - Clang's Rewriter system (no string manipulation)
/// - Semantic analysis (proper type handling)
/// - XC8 architecture (extensible design)
class CppToCCheck : public ClangTidyCheck {
public:
  CppToCCheck(StringRef Name, ClangTidyContext *Context)
      : ClangTidyCheck(Name, Context) {}
  
  // Register AST matchers - declarative pattern matching!
  void registerMatchers(ast_matchers::MatchFinder *Finder) override;
  
  // Process matched nodes - semantic transformation!
  void check(const ast_matchers::MatchFinder::MatchResult &Result) override;

private:
  // XC8 transformation methods using Clang's APIs
  void transformClass(const CXXRecordDecl *ClassDecl, 
                      const ast_matchers::MatchFinder::MatchResult &Result);
  
  void transformMethod(const CXXMethodDecl *MethodDecl,
                       const ast_matchers::MatchFinder::MatchResult &Result);
  
  void transformConstructor(const CXXConstructorDecl *ConstructorDecl,
                            const ast_matchers::MatchFinder::MatchResult &Result);
  
  void transformDestructor(const CXXDestructorDecl *DestructorDecl,
                           const ast_matchers::MatchFinder::MatchResult &Result);
  
  void transformMemberCall(const CXXMemberCallExpr *MemberCall,
                           const ast_matchers::MatchFinder::MatchResult &Result);
};

} // namespace xc8
} // namespace tidy
} // namespace clang

#endif // LLVM_CLANG_TOOLS_EXTRA_CLANG_TIDY_XC8_CPPTOCCHECK_H
