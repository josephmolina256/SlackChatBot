

# Common FAQs 

## **Logistics**

*What compiler should we use?*

* The course officially supports VSCode and the MinGW compiler. Meaning all TAs should be able to help you out with installation.   
* We will also provide debugging tips and resources that are made to support VSCode   
* Despite this, you are free to use whatever IDE/compiler you’re comfortable with 

*Can we use an IDE while coding on Stepik?*

* Yes, however, be sure to test the code on Stepik before submitting, as the code may behave differently  
* Keep in mind that Stepik uses the g++ 6.3.0 compiler, with at least C++ 11 features

*Can you have paper on the quizzes?*

* Yes, you may have blank paper for the quiz.

*Can I use Java for free response coding questions?*

* No, "For the exams \[and quizzes\], you can use C++ or pseudo code to describe your solution to a given problem." \- Syllabus.   
* I recommend having your code look more like pseudo code rather than C++ though for readability and saving you time on not having to worry about syntax.

*Is there a free response coding question on "Quiz 2 \- Algorithm Analysis"?*

* Yes. Please review the latter portion of the discussion sllides/recording for some tips on how to write pseudocode. Avoid writing paragraphs\!\!\!\! Pseudo code should structured and indented like code.

*When must we complete Stepik questions?*

* You can see the individually assigned stepik questions under the assignments and their respective due dates.  
* All quiz related stepik questions are due by their respective quiz due dates.

*Should we be able to join Stepik yet?*

* Yes, if you filled out the survey you should be getting added to stepik shortly. Many students who filled out the survey should have already been added.   
* Make sure to check your email and spam folders for the invite.

## **C++**

*Should you pass vectors by value or by reference?*

* To avoid making a copy of the entire vector, always pass vectors as reference parameters. [http://www.fredosaurus.com/notes-cpp/stl-containers/vector/vector-parameters.html](http://www.fredosaurus.com/notes-cpp/stl-containers/vector/vector-parameters.html)


*Is there a name for an error with memory leaks?*

* Memory leaks can cause you to run out of memory on the heap which results in the program prematurely terminating (either gracefully or as a crash).   
* From my research, the parralel error to Java's Out of Memory error is std::bad\_alloc. [https://www.cprogramming.com/tutorial/memory\_debugging\_parallel\_inspector.html](https://www.cprogramming.com/tutorial/memory_debugging_parallel_inspector.html)  
* [https://stackoverflow.com/questions/7749066/how-to-catch-out-of-memory-exception-in-c/13327733](https://stackoverflow.com/questions/7749066/how-to-catch-out-of-memory-exception-in-c/13327733)


*Memory management \- how much can you allocate on the heap?*

* The default heap size is 1 MB. You cannot allocate more memory than you have available. For visual studio, you can set the size of the heap like in the first StackOverflow link below.  
* [https://stackoverflow.com/questions/28653477/self-limit-heap-size-in-c](https://stackoverflow.com/questions/28653477/self-limit-heap-size-in-c)  
* [https://docs.microsoft.com/en-us/cpp/build/reference/heap-set-heap-size?view=msvc-160](https://docs.microsoft.com/en-us/cpp/build/reference/heap-set-heap-size?view=msvc-160)  
* [https://stackoverflow.com/questions/12411966/maximum-memory-for-stack-static-and-heap-memory-in-c](https://stackoverflow.com/questions/12411966/maximum-memory-for-stack-static-and-heap-memory-in-c)

*Segmentation faults and dangling pointers:*

* Segmentation faults occur when you try to set memory that does not belong to you. Undefined behavior can occur when you try to access memory that does not belong to you. Using dangling pointers does not always result in segmentation faults.  
* [https://www.geeksforgeeks.org/accessing-array-bounds-ccpp/](https://www.geeksforgeeks.org/accessing-array-bounds-ccpp/)  
* [https://www.educative.io/edpresso/learning-about-segmentation-faults-in-cpp](https://www.educative.io/edpresso/learning-about-segmentation-faults-in-cpp)  
* [https://stackoverflow.com/questions/2346806/what-is-a-segmentation-fault](https://stackoverflow.com/questions/2346806/what-is-a-segmentation-fault)  
* Using dangling pointers results in undefined behavior. If you try to dereference a dangling pointer to memory that has been reallocated to another process, you will get a segmentation fault on UNIX/Linux environments or a general protection fault on Windows. [https://en.wikipedia.org/wiki/Dangling\_pointer](https://en.wikipedia.org/wiki/Dangling_pointer)

## 

## **Stepik**

*What Stepik problems are assigned? And when are they due?* 

* Stepik problems are listed in Assignments on Canvas, under the section “Preassigned Stepik Questions”  
* Clicking on a section shows the due date and problem(s) assigned.   
* You are ONLY required to do listed problems. Non-listed problems are good practice, but will not be graded  
* Each problem is denoted by a three digit value: Module.Problem.Step

## 

## **Algorithm Analysis**

*How do you derive the time complexity of code like:*  
for (int i \= n; i \>= 0; i--)  
    for (int j \= 0; j \<= i; j++)  
        // O(1) thing

* First iteration of outer for loop results in n iterations of the inner loop.  
* Second iteration of outer for loop results in n-1 iterations of the inner loop.  
* ...  
* Nth iteration of outer for loop results in 1 iteration of the inner loop.  
* n \+ (n-1) \+ ... \+ 2 \+ 1 \= n (n+1) / 2 \= O(n^2)  
* [https://stackoverflow.com/questions/44252596/big-o-complexity-for-n-n-1-n-2-n-3-1/44255732](https://stackoverflow.com/questions/44252596/big-o-complexity-for-n-n-1-n-2-n-3-1/44255732)

*What happens when you have nested log(n) loops?*  
A: [https://stackoverflow.com/questions/14473684/java-big-o-notation-of-3-nested-loops-of-logn](https://stackoverflow.com/questions/14473684/java-big-o-notation-of-3-nested-loops-of-logn)