#!/usr/bin/env python3

import os
import sys
import requests
import json
from bs4 import BeautifulSoup

# If you run the Node-based alfaarghya/alfa-leetcode-api locally, set the endpoint here:
LEETCODE_API_URL = "http://localhost:3000"  # or wherever your Node service is running


def prompt_for_int(prompt_message, default=None):
    """
    Safely prompt for an integer from the user.
    If default is provided, pressing enter yields that default.
    """
    while True:
        user_input = input(prompt_message).strip()
        if not user_input and default is not None:
            return default
        try:
            return int(user_input)
        except ValueError:
            print("Invalid integer. Please try again.")


def get_leetcode_problem(problem_id):
    """
    Placeholder function to retrieve a LeetCode problem by ID,
    by querying a local Node server (alfaarghya/alfa-leetcode-api) if it's running.

    Returns a dict with 'title', 'difficulty', 'content' or None on failure.
    """
    try:
        # Example endpoint: GET /problems/:id
        # Adjust if your Node app has a different route.
        url = f"{LEETCODE_API_URL}/problems/{problem_id}"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"[Warning] Could not retrieve LeetCode problem from Node API. Status code: {resp.status_code}")
            return None
        data = resp.json()
        # You must adapt the parsing here based on how your Node server returns data:
        # For instance, if the JSON looks like:
        # {
        #   "title": "Roman to Integer",
        #   "difficulty": "Easy",
        #   "content": "<p>Some HTML</p>"
        # }
        # then you can directly extract:

        title = data.get("title", "")
        difficulty = data.get("difficulty", "")
        content = data.get("content", "")  # HTML

        if not title:
            # minimal validation
            return None

        return {
            "title": title,
            "difficulty": difficulty,
            "content": content
        }
    except requests.exceptions.RequestException as e:
        print(f"[Warning] LeetCode Node server request failed: {e}")
        return None


def parse_codeforces_contest_and_index(user_input):
    """
    Given a string like '4A' -> contestId=4, index='A'
    e.g. '1000B' -> 1000, 'B'
    If invalid, returns (None, None).
    """
    digits_part = ""
    index_part = ""
    for char in user_input:
        if char.isdigit():
            digits_part += char
        else:
            index_part += char
    if not digits_part or not index_part:
        return None, None
    return int(digits_part), index_part


def codeforces_api_fetch(contest_id, problem_index):
    """
    Fetch some metadata (title, tags) from the official Codeforces API.
    """
    try:
        url = "https://codeforces.com/api/problemset.problems"
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("status") != "OK":
            print("[Error] Codeforces API did not respond with status=OK.")
            return None

        for p in data["result"]["problems"]:
            if p["contestId"] == contest_id and p["index"] == problem_index:
                return {
                    "title": p.get("name", ""),
                    "tags": p.get("tags", []),
                }
        return None
    except requests.exceptions.RequestException as e:
        print("[Error] While contacting Codeforces API:", e)
        return None


def scrape_codeforces_statement(contest_id, problem_index):
    """
    Scrape the problem statement from the Codeforces page:
    https://codeforces.com/contest/<contest_id>/problem/<problem_index>
    Returns a string (HTML or partial text) or None if failed.
    """
    url = f"https://codeforces.com/contest/{contest_id}/problem/{problem_index}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"[Warning] Could not scrape Codeforces statement: HTTP {resp.status_code}")
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        statement_div = soup.find('div', class_='problem-statement')
        if not statement_div:
            return None
        # Extract the text or keep some HTML
        return statement_div.get_text(separator="\n").strip()
    except requests.exceptions.RequestException as e:
        print("[Error] While scraping Codeforces statement:", e)
        return None


def scrape_vjudge_statement(oj_problem):
    """
    For VJudge, the input might look like 'LightOJ-1000'.
    We'll build a URL: https://vjudge.net/problem/LightOJ-1000
    Then scrape the problem statement from that page.
    Returns text or None if not found.
    """
    url = f"https://vjudge.net/problem/{oj_problem}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"[Warning] Could not scrape VJudge statement: HTTP {resp.status_code}")
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        # VJudge pages are dynamic, sometimes the statement is loaded by JavaScript.
        # We'll attempt to find some typical container. This is not guaranteed to always work.
        statement_div = soup.find('div', class_='panel-body')
        if not statement_div:
            # fallback
            return None
        return statement_div.get_text(separator="\n").strip()
    except requests.exceptions.RequestException as e:
        print("[Error] While scraping VJudge statement:", e)
        return None


def main():
    print("Welcome to the Competitive Programming Problem Setup!\n")

    # 1) Ask for problem type
    print("Select the problem source:")
    print("1) LeetCode")
    print("2) Codeforces")
    print("3) VJudge")
    print("4) Custom")

    while True:
        user_choice = input("Enter your choice (1-4): ").strip()
        if user_choice in ["1", "2", "3", "4"]:
            problem_type = int(user_choice)
            break
        print("Invalid choice, please select 1, 2, 3, or 4.")

    folder_name = ""
    problem_metadata = {}

    # ------------------------------------------------------
    # LEETCODE
    # ------------------------------------------------------
    if problem_type == 1:
        problem_id = prompt_for_int("Enter the LeetCode problem ID (e.g., 13): ")
        print(f"Fetching LeetCode problem #{problem_id}...")
        ld = get_leetcode_problem(problem_id)
        if ld is None:
            print("[Warning] LeetCode data not found, Node server not running, or authentication missing. Creating folder anyway.")
            folder_name = f"leetcode_p{problem_id}"
        else:
            folder_name = f"leetcode_p{problem_id}"
            problem_metadata["title"] = ld["title"]
            problem_metadata["difficulty"] = ld["difficulty"]
            problem_metadata["statement"] = ld["content"]  # HTML

    # ------------------------------------------------------
    # CODEFORCES
    # ------------------------------------------------------
    elif problem_type == 2:
        cf_input = input("Enter Codeforces problem in 'contestId+index' format (e.g. '4A'): ").strip()
        contest_id, problem_index = parse_codeforces_contest_and_index(cf_input)
        if not contest_id or not problem_index:
            print(f"[Warning] '{cf_input}' is not valid. Creating folder anyway.")
            folder_name = f"codeforces_p{cf_input}"
        else:
            folder_name = f"codeforces_p{contest_id}{problem_index}"
            # Official API fetch
            meta = codeforces_api_fetch(contest_id, problem_index)
            if meta:
                problem_metadata["title"] = meta["title"]
                problem_metadata["tags"] = ", ".join(meta["tags"])
            # Now scrape statement
            statement = scrape_codeforces_statement(contest_id, problem_index)
            if statement:
                problem_metadata["statement"] = statement
            else:
                print("[Warning] Could not scrape Codeforces statement.")

    # ------------------------------------------------------
    # VJUDGE
    # ------------------------------------------------------
    elif problem_type == 3:
        # Expect something like "LightOJ-1000"
        oj_problem = input("Enter VJudge problem in '<OJ>-<ProblemID>' format (e.g., 'LightOJ-1000'): ").strip()
        if not oj_problem:
            print("[Warning] No input. Creating folder anyway.")
            folder_name = "vjudge_problem_untitled"
        else:
            folder_name = f"vjudge_problem_{oj_problem.lower().replace('-', '')}"
            statement = scrape_vjudge_statement(oj_problem)
            if statement:
                problem_metadata["title"] = oj_problem
                problem_metadata["statement"] = statement
            else:
                print("[Warning] Could not retrieve VJudge statement. Possibly requires login or page changed.")

    # ------------------------------------------------------
    # CUSTOM
    # ------------------------------------------------------
    else:
        while True:
            custom_name = input("Enter a name for the custom problem folder: ").strip()
            if custom_name:
                folder_name = custom_name
                break
            print("Folder name cannot be empty.")

    # ------------------------------------------------------
    # Choose language
    # ------------------------------------------------------
    print("\nSelect language:")
    print("1) C++")
    print("2) C")
    print("3) Python")
    print("4) Java")

    while True:
        lang_choice = input("Enter your choice (1-4): ").strip()
        if lang_choice in ["1", "2", "3", "4"]:
            lang_choice = int(lang_choice)
            break
        print("Invalid choice, please select 1, 2, 3, or 4.")

    if lang_choice == 1:
        language = "cpp"
        default_filename = "main.cpp"
    elif lang_choice == 2:
        language = "c"
        default_filename = "main.c"
    elif lang_choice == 3:
        language = "py"
        default_filename = "main.py"
    else:
        language = "java"
        default_filename = "Main.java"

    filename = input(f"Enter the name of the file (default: {default_filename}): ").strip()
    if not filename:
        filename = default_filename

    # ------------------------------------------------------
    # Skeleton type
    # ------------------------------------------------------
    print("\nWhich skeleton type would you like?")
    print("1) Extended")
    print("2) Minimal")

    while True:
        skeleton_choice = input("Enter your choice (1-2): ").strip()
        if skeleton_choice in ["1", "2"]:
            skeleton_type = int(skeleton_choice)
            break
        print("Invalid choice, please select 1 or 2.")

    # Extended skeleton details (for C++ and Java specifically)
    extended_args = {
        "class_name": "",
        "return_type": "",
        "function_name": "",
        "arguments": []
    }

    if skeleton_type == 1:
        if language == "cpp":
            extended_args["class_name"] = input("Enter the class name (default: 'Solution'): ").strip() or "Solution"
            extended_args["return_type"] = input("Enter the return type (default: 'int'): ").strip() or "int"
            extended_args["function_name"] = input("Enter the function name (default: 'test'): ").strip() or "test"
            arg_count = prompt_for_int("Enter the number of arguments (default: 0): ", default=0)
            for i in range(arg_count):
                at = input(f"Enter type for argument #{i+1} (e.g., 'int', 'string'): ").strip() or "int"
                extended_args["arguments"].append(at)
        elif language == "java":
            extended_args["class_name"] = input("Enter the class name (default: 'Solution'): ").strip() or "Solution"
            extended_args["return_type"] = input("Enter the return type (default: 'int'): ").strip() or "int"
            extended_args["function_name"] = input("Enter the function name (default: 'test'): ").strip() or "test"
            arg_count = prompt_for_int("Enter the number of arguments (default: 0): ", default=0)
            for i in range(arg_count):
                at = input(f"Enter type for argument #{i+1} (e.g., 'int', 'String'): ").strip() or "int"
                extended_args["arguments"].append(at)
        # For Python or C, we won't do an elaborate function signature prompt.
        # But you can extend that here if you wish.

    # ------------------------------------------------------
    # Create the folder
    # ------------------------------------------------------
    try:
        os.makedirs(folder_name, exist_ok=True)
    except OSError as e:
        print(f"[Error] Unable to create folder '{folder_name}': {e}")
        sys.exit(1)

    file_path = os.path.join(folder_name, filename)

    # ------------------------------------------------------
    # Generate code
    # ------------------------------------------------------
    code_lines = []

    # If we have metadata, add it as a comment
    if problem_metadata:
        code_lines.append("// ===================================")
        code_lines.append("// Problem Metadata")
        for k, v in problem_metadata.items():
            if k == "statement" and len(v) > 300:
                # Truncate if very large (especially HTML)
                snippet = v[:300].replace("\n", " ") + "..."
                code_lines.append(f"// {k} (truncated): {snippet}")
            else:
                # For multi-line statements, break them up as separate comment lines
                lines = v.splitlines()
                code_lines.append(f"// {k}:")
                for line in lines:
                    code_lines.append(f"//    {line}")
        code_lines.append("// ===================================\n")

    # Minimal or Extended skeleton
    if language == "cpp":
        if skeleton_type == 2:
            # Minimal
            code_lines.append("#include <iostream>")
            code_lines.append("using namespace std;\n")
            code_lines.append("int main() {")
            code_lines.append("    return 0;")
            code_lines.append("}")
        else:
            # Extended
            cn = extended_args["class_name"]
            rt = extended_args["return_type"]
            fn = extended_args["function_name"]
            args = extended_args["arguments"]

            code_lines.append("#include <iostream>")
            code_lines.append("#include <vector>")
            code_lines.append("using namespace std;\n")
            code_lines.append(f"class {cn} {{")
            code_lines.append("public:")
            # Build function signature
            if args:
                # e.g. "int test(int a1, string a2)"
                arg_list = []
                for i, a in enumerate(args):
                    arg_list.append(f"{a} arg{i+1}")
                arg_str = ", ".join(arg_list)
                code_lines.append(f"    {rt} {fn}({arg_str}) {{")
            else:
                code_lines.append(f"    {rt} {fn}() {{")

            code_lines.append("        // TODO: implement function logic here")
            if rt != "void":
                if rt == "int":
                    code_lines.append("        return 0;")
                else:
                    code_lines.append(f"        {rt} defaultVal = {{}}; // or other initialization")
                    code_lines.append("        return defaultVal;")
            code_lines.append("    }")
            code_lines.append("};\n")
            code_lines.append("// Testing Function")
            code_lines.append("int main() {")
            code_lines.append(f"    {cn} sol;")
            if args:
                dummy_args = []
                for a in args:
                    if a == "int":
                        dummy_args.append("0")
                    elif a in ("string", "std::string"):
                        dummy_args.append("\"\"")
                    else:
                        dummy_args.append(f"/* {a} */")
                call_line = f"    auto result = sol.{fn}({', '.join(dummy_args)});"
                code_lines.append(call_line)
                if rt != "void":
                    code_lines.append("    cout << \"Result: \" << result << endl;")
            else:
                call_line = f"    auto result = sol.{fn}();"
                code_lines.append(call_line)
                if rt != "void":
                    code_lines.append("    cout << \"Result: \" << result << endl;")
            code_lines.append("    return 0;")
            code_lines.append("}")
    elif language == "c":
        if skeleton_type == 2:
            # Minimal
            code_lines.append("#include <stdio.h>\n")
            code_lines.append("int main() {")
            code_lines.append("    return 0;")
            code_lines.append("}")
        else:
            # Extended approach in C is less typical, but let's do a simple struct + function
            code_lines.append("#include <stdio.h>")
            code_lines.append("#include <stdlib.h>\n")
            code_lines.append("typedef struct {")
            code_lines.append("    // You can store fields here if needed")
            code_lines.append("} Solution;\n")
            code_lines.append("int testFunction(Solution* sol) {")
            code_lines.append("    // Implement logic")
            code_lines.append("    return 0;")
            code_lines.append("}\n")
            code_lines.append("int main() {")
            code_lines.append("    Solution sol;")
            code_lines.append("    int result = testFunction(&sol);")
            code_lines.append("    printf(\"Result: %d\\n\", result);")
            code_lines.append("    return 0;")
            code_lines.append("}")
    elif language == "py":
        if skeleton_type == 2:
            # Minimal
            code_lines.append("#!/usr/bin/env python3")
            code_lines.append("def main():")
            code_lines.append("    pass  # TODO: solve the problem here")
            code_lines.append("")
            code_lines.append("if __name__ == '__main__':")
            code_lines.append("    main()")
        else:
            # Extended: We'll do a simple approach with a solve() function
            code_lines.append("#!/usr/bin/env python3")
            code_lines.append("def solve(*args):")
            code_lines.append("    # TODO: implement logic")
            code_lines.append("    return 0  # or something else\n")
            code_lines.append("def main():")
            code_lines.append("    # Example usage of solve()")
            code_lines.append("    result = solve()")
            code_lines.append("    print(f\"Result: {result}\")")
            code_lines.append("")
            code_lines.append("if __name__ == '__main__':")
            code_lines.append("    main()")
    else:
        # Java
        if skeleton_type == 2:
            # Minimal
            code_lines.append("public class Main {")
            code_lines.append("    public static void main(String[] args) {")
            code_lines.append("        // TODO: implement solution")
            code_lines.append("    }")
            code_lines.append("}")
        else:
            # Extended: separate Solution class, plus a Main class
            cn = extended_args["class_name"]
            rt = extended_args["return_type"]
            fn = extended_args["function_name"]
            args = extended_args["arguments"]

            code_lines.append("public class Main {")
            code_lines.append("    public static void main(String[] args) {")
            code_lines.append(f"        {cn} sol = new {cn}();")
            if args:
                dummy_args = []
                for a in args:
                    if a == "int":
                        dummy_args.append("0")
                    elif a == "String":
                        dummy_args.append("\"\"")
                    else:
                        dummy_args.append(f"/* {a} */")
                call_line = f"        {rt} result = sol.{fn}({', '.join(dummy_args)});"
                code_lines.append(call_line)
                if rt != "void":
                    code_lines.append("        System.out.println(\"Result: \" + result);")
            else:
                call_line = f"        {rt} result = sol.{fn}();"
                code_lines.append(call_line)
                if rt != "void":
                    code_lines.append("        System.out.println(\"Result: \" + result);")
            code_lines.append("    }")
            code_lines.append("}\n")

            # Now define the solution class
            code_lines.append(f"class {cn} {{")
            if args:
                # e.g. "public int test(int a1, String a2)"
                arg_list = []
                for i, a in enumerate(args):
                    arg_list.append(f"{a} arg{i+1}")
                arg_str = ", ".join(arg_list)
                code_lines.append(f"    public {rt} {fn}({arg_str}) {{")
            else:
                code_lines.append(f"    public {rt} {fn}() {{")

            code_lines.append("        // TODO: implement logic here")
            if rt != "void":
                if rt == "int":
                    code_lines.append("        return 0;")
                elif rt == "String":
                    code_lines.append("        return \"\";")
                else:
                    code_lines.append("        // Return some default value")
                    code_lines.append("        return null;")
            code_lines.append("    }")
            code_lines.append("}")

    # ------------------------------------------------------
    # Write to file
    # ------------------------------------------------------
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for line in code_lines:
                f.write(line + "\n")
        print(f"Successfully created '{file_path}' with the desired skeleton.")
    except OSError as e:
        print(f"[Error] Writing to file {file_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

