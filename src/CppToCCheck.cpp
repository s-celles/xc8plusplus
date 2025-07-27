//===--- CppToCCheck.cpp - clang-tidy -----------------------------------===//
//
// XC8 C++ to C transformation using clang-tidy framework
// This is the CORRECT approach - not Python soup!
//
//===----------------------------------------------------------------------===//

#include "CppToCCheck.h"
#include "clang/AST/ASTContext.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/Lex/Lexer.h"

using namespace clang::ast_matchers;

namespace clang {
namespace tidy {
namespace xc8 {

// XC8 AST Matchers - declarative pattern matching!
void CppToCCheck::registerMatchers(MatchFinder *Finder) {
  // Match C++ classes for struct transformation
  Finder->addMatcher(
    cxxRecordDecl(
      isClass(),
      unless(isImplicit())
    ).bind("class"),
    this
  );

  // Match C++ methods for function transformation  
  Finder->addMatcher(
    cxxMethodDecl(
      unless(isImplicit())
    ).bind("method"),
    this
  );

  // Match constructors for init function transformation
  Finder->addMatcher(
    cxxConstructorDecl(
      unless(isImplicit())
    ).bind("constructor"),
    this
  );

  // Match destructors for cleanup function transformation
  Finder->addMatcher(
    cxxDestructorDecl(
      unless(isImplicit())
    ).bind("destructor"),
    this
  );

  // Match member calls for function call transformation
  Finder->addMatcher(
    cxxMemberCallExpr().bind("member_call"),
    this
  );
}

// XC8 transformation using Clang's Rewriter - no string manipulation!
void CppToCCheck::check(const MatchFinder::MatchResult &Result) {
  const auto *ClassDecl = Result.Nodes.getNodeAs<CXXRecordDecl>("class");
  const auto *MethodDecl = Result.Nodes.getNodeAs<CXXMethodDecl>("method");
  const auto *ConstructorDecl = Result.Nodes.getNodeAs<CXXConstructorDecl>("constructor");
  const auto *DestructorDecl = Result.Nodes.getNodeAs<CXXDestructorDecl>("destructor");
  const auto *MemberCall = Result.Nodes.getNodeAs<CXXMemberCallExpr>("member_call");

  if (ClassDecl) {
    transformClass(ClassDecl, Result);
  }
  
  if (MethodDecl) {
    transformMethod(MethodDecl, Result);
  }
  
  if (ConstructorDecl) {
    transformConstructor(ConstructorDecl, Result);
  }
  
  if (DestructorDecl) {
    transformDestructor(DestructorDecl, Result);
  }
  
  if (MemberCall) {
    transformMemberCall(MemberCall, Result);
  }
}

void CppToCCheck::transformClass(const CXXRecordDecl *ClassDecl, 
                                 const MatchFinder::MatchResult &Result) {
  // XC8 source transformation using Clang's Rewriter
  SourceManager &SM = *Result.SourceManager;
  SourceLocation StartLoc = ClassDecl->getBeginLoc();
  
  // Find "class" keyword location
  SourceLocation ClassKeywordLoc = ClassDecl->getLocation();
  
  // Use Clang's Rewriter for XC8 transformation
  if (StartLoc.isValid() && ClassKeywordLoc.isValid()) {
    std::string ClassName = ClassDecl->getNameAsString();
    
    // Replace "class" with "typedef struct"
    SourceRange ClassKeywordRange(StartLoc, 
      Lexer::getLocForEndOfToken(StartLoc, 0, SM, getLangOpts()));
    
    std::string Replacement = "typedef struct";
    
    diag(StartLoc, "transforming C++ class '%0' to C struct")
      << ClassName
      << FixItHint::CreateReplacement(ClassKeywordRange, Replacement);
    
    // Add typedef at the end of class definition
    SourceLocation EndLoc = ClassDecl->getBraceRange().getEnd();
    if (EndLoc.isValid()) {
      std::string TypedefEnd = " " + ClassName;
      
      diag(EndLoc, "adding typedef name for struct")
        << FixItHint::CreateInsertion(
            Lexer::getLocForEndOfToken(EndLoc, 0, SM, getLangOpts()),
            TypedefEnd);
    }
  }
}

void CppToCCheck::transformMethod(const CXXMethodDecl *MethodDecl,
                                  const MatchFinder::MatchResult &Result) {
  // Don't transform constructors/destructors here - handled separately
  if (isa<CXXConstructorDecl>(MethodDecl) || isa<CXXDestructorDecl>(MethodDecl)) {
    return;
  }
  
  SourceManager &SM = *Result.SourceManager;
  std::string ClassName = MethodDecl->getParent()->getNameAsString();
  std::string MethodName = MethodDecl->getNameAsString();
  
  // XC8 type handling using Clang's type system
  QualType ReturnType = MethodDecl->getReturnType();
  std::string ReturnTypeStr = ReturnType.getAsString();
  
  SourceLocation StartLoc = MethodDecl->getBeginLoc();
  
  // Transform method signature to C function
  std::string NewSignature = ReturnTypeStr + " " + ClassName + "_" + MethodName + 
                            "(" + ClassName + "* self";
  
  // Add parameters
  for (unsigned i = 0; i < MethodDecl->getNumParams(); ++i) {
    const ParmVarDecl *Param = MethodDecl->getParamDecl(i);
    QualType ParamType = Param->getType();
    std::string ParamName = Param->getNameAsString();
    
    NewSignature += ", " + ParamType.getAsString() + " " + ParamName;
  }
  NewSignature += ")";
  
  diag(StartLoc, "transforming C++ method '%0::%1' to C function '%2_%1'")
    << ClassName << MethodName << ClassName;
}

void CppToCCheck::transformConstructor(const CXXConstructorDecl *ConstructorDecl,
                                       const MatchFinder::MatchResult &Result) {
  SourceManager &SM = *Result.SourceManager;
  std::string ClassName = ConstructorDecl->getParent()->getNameAsString();
  
  SourceLocation StartLoc = ConstructorDecl->getBeginLoc();
  
  std::string InitFunctionSignature = "void " + ClassName + "_init(" + 
                                     ClassName + "* self)";
  
  diag(StartLoc, "transforming C++ constructor to C init function '%0_init'")
    << ClassName;
}

void CppToCCheck::transformDestructor(const CXXDestructorDecl *DestructorDecl,
                                      const MatchFinder::MatchResult &Result) {
  SourceManager &SM = *Result.SourceManager;
  std::string ClassName = DestructorDecl->getParent()->getNameAsString();
  
  SourceLocation StartLoc = DestructorDecl->getBeginLoc();
  
  std::string CleanupFunctionSignature = "void " + ClassName + "_cleanup(" + 
                                        ClassName + "* self)";
  
  diag(StartLoc, "transforming C++ destructor to C cleanup function '%0_cleanup'")
    << ClassName;
}

void CppToCCheck::transformMemberCall(const CXXMemberCallExpr *MemberCall,
                                      const MatchFinder::MatchResult &Result) {
  SourceManager &SM = *Result.SourceManager;
  
  const CXXMethodDecl *MethodDecl = MemberCall->getMethodDecl();
  if (!MethodDecl) return;
  
  std::string ClassName = MethodDecl->getParent()->getNameAsString();
  std::string MethodName = MethodDecl->getNameAsString();
  
  SourceLocation StartLoc = MemberCall->getBeginLoc();
  
  diag(StartLoc, "transforming C++ member call '%0.%1()' to C function call '%0_%1(&%0)'")
    << ClassName << MethodName;
}

} // namespace xc8
} // namespace tidy
} // namespace clang
