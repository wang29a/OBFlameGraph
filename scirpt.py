import os
import subprocess
import signal
import time
import argparse
from datetime import datetime

def log_message(message: str):
    """
    打印日志消息
    """
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")

def get_commit_id(repo_path="."):
    """
    获取指定目录下 Git 仓库的最新 commit ID。
    
    :param repo_path: Git 仓库路径，默认为当前目录。
    :return: 最新 commit ID 或 "unknown_commit_id"（如果获取失败）。
    """
    try:
        # 保存当前工作目录
        original_dir = os.getcwd()
        # 切换到指定目录
        os.chdir(repo_path)
        
        # 执行 Git 命令获取 commit ID
        result = subprocess.run(
            "git rev-parse HEAD",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 切换回原来的工作目录
        os.chdir(original_dir)

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"Failed to get commit ID: {result.stderr}")
            return "unknown_commit_id"
    except Exception as e:
        print(f"Error getting commit ID: {e}")
        return "unknown_commit_id"


def create_folder_and_readme(folder_name, readme_content):
    """
    创建文件夹并生成 README.md 文件
    """
    os.makedirs(folder_name, exist_ok=True)
    readme_path = os.path.join(folder_name, "README.md")
    with open(readme_path, "w") as f:
        f.write(readme_content)
    log_message(f"Folder '{folder_name}' created with README.md")

def run_commands(perf_command, python_command):
    try:
        log_message(f"Starting perf command: {' '.join(perf_command)}")
        perf_process = subprocess.Popen(perf_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        log_message(f"Running Python script: {' '.join(python_command)}")
        subprocess.run(python_command, text=True, check=True)

        time.sleep(5)  # 等待 perf 运行稳定
        if perf_process.poll() is None:
            os.kill(perf_process.pid, signal.SIGINT)  # 中断 perf
            log_message("Perf process terminated.")
    except Exception as e:
        log_message(f"Error occurred during command execution: {e}")
    finally:
        if perf_process.poll() is None:
            pass
            # os.kill(perf_process.pid, signal.SIGKILL)  # 强制终止
            # log_message("Perf process forcefully terminated.")


def run(port, skip):
    path = "/root/source/OBFlameGraph/"
    repo_path_1 = "/root/source/ann-benchmarks/"
    original_dir = os.getcwd()
    # 定义两个命令
    perf_command_basic = [
        ["perf", "record", "-o", path+"basic1.data", "-F", "99", "-p", f"{port}", "-a", "-g"],
        ["perf", "record", "-o", path+"basic2.data", "-F", "99", "-p", f"{port}", "-a", "-g"]
    ]
    perf_command_sql = [
        ["perf", "record", "-o", path+"sql.data", "-F", "99", "-p", f"{port}", "-a", "-g"],
        ["perf", "record", "-o", path+"sql1.data", "-F", "99", "-p", f"{port}", "-a", "-g"],
        ["perf", "record", "-o", path+"sql2.data", "-F", "99", "-p", f"{port}", "-a", "-g"],
        ["perf", "record", "-o", path+"sql3.data", "-F", "99", "-p", f"{port}", "-a", "-g"]
    ]
    python_command = ["python", "/root/source/ann-benchmarks/run.py", "--algorithm", "oceanbase", "--local", "--force", "--dataset", "sift-128-euclidean", "--runs", "1"]
    python_command_skip_fit = ["python", "/root/source/ann-benchmarks/run.py", "--algorithm", "oceanbase", "--local", "--force", "--dataset", "sift-128-euclidean", "--runs", "1", "--skip_fit"]
    python_command_sql = [
        ["python", "-m", "ann_benchmarks.algorithms.oceanbase.hybrid_ann", "--skip_fit"],
        ["python", "-m", "ann_benchmarks.algorithms.oceanbase.hybrid_ann", "--skip_fit", "--queries", "sql1"],
        ["python", "-m", "ann_benchmarks.algorithms.oceanbase.hybrid_ann", "--skip_fit", "--queries", "sql2"],
        ["python", "-m", "ann_benchmarks.algorithms.oceanbase.hybrid_ann", "--skip_fit", "--queries", "sql3"],
    ]
    # 切换到指定目录
    os.chdir(repo_path_1)
    if (not skip):
        run_commands(perf_command_basic[0], python_command)
    run_commands(perf_command_basic[1], python_command_skip_fit)
    for i in range(0, 4):
        run_commands(perf_command_sql[i], python_command_sql[i])
    os.chdir(original_dir)

def parse_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description="Run two commands and manage their execution with a number parameter.")
    parser.add_argument(
        "--pid", 
        type=int, 
        required=True, 
        help="obsever pid"
    )
    parser.add_argument(
        "--skip-fit", 
        action="store_true", 
        help="If set, skip the fit process"
    )
    return parser.parse_args()

def generate_flamegraph(data_file, output_svg, flamegraph_dir):
    """
    使用 perf 数据生成火焰图。
    
    :param data_file: perf 数据文件路径 (e.g., "sql1.data")。
    :param output_svg: 输出 SVG 文件路径 (e.g., "sql1.svg")。
    :param flamegraph_dir: FlameGraph 工具的路径 (e.g., "FlameGraph")。
    """
    # 检查输入文件是否存在
    if not os.path.exists(data_file):
        print(f"Error: Data file '{data_file}' does not exist.")
        return

    # 检查 FlameGraph 工具路径是否存在
    stackcollapse_path = os.path.join(flamegraph_dir, "stackcollapse-perf.pl")
    flamegraph_path = os.path.join(flamegraph_dir, "flamegraph.pl")

    if not os.path.exists(stackcollapse_path) or not os.path.exists(flamegraph_path):
        print(f"Error: FlameGraph tools not found in '{flamegraph_dir}'.")
        return

    try:
        # 构建命令
        command = f"perf script -i {data_file} | {stackcollapse_path} | {flamegraph_path} > {output_svg}"

        # 执行命令
        print(f"Running command: {command}")
        subprocess.run(command, shell=True, check=True, text=True)
        print(f"Flamegraph generated successfully: {output_svg}")

    except subprocess.CalledProcessError as e:
        print(f"Error while running command: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def execute_command_and_save(port, skip):
    """
    执行命令并将输出保存到文件中
    """
    data_files = ["basic1.data", "basic2.data", "sql.data", "sql1.data", "sql2.data", "sql3.data"]
    output_svgs = [f.replace(".data", ".svg") for f in data_files]
    flamegraph_dir = "/root/source/FlameGraph/"

    # 跳过 fit 时调整处理数据集
    data_files = data_files[1:] if skip else data_files
    output_svgs = output_svgs[1:] if skip else output_svgs

    for data_file, output_svg in zip(data_files, output_svgs):
        generate_flamegraph(data_file, output_svg, flamegraph_dir)



def main(args):
    run(args.pid, args.skip_fit)
    execute_command_and_save(args.pid, args.skip_fit)
    
    # 获取日期和最新 commit ID
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    repo_path = "/root/source/OceanBase"  # 替换为你的 Git 仓库路径
    commit_id = get_commit_id(repo_path)
    
    # 创建文件夹
    folder_name = f"{current_date}-{commit_id}"
    readme_content = f"# Folder Info\n\n- Date: {current_date}\n- Commit ID: {commit_id}\n"
    create_folder_and_readme(folder_name, readme_content)
    
    # 移动文件到新文件夹
    if (not args.skip_fit):
        output_svg = ["basic1.svg","basic2.svg", "sql.svg", "sql1.svg", "sql2.svg", "sql3.svg"]  # 输出的 SVG 文件
        for i in output_svg:
            os.rename(i, os.path.join(folder_name, i))
    else:
        output_svg = ["basic2.svg", "sql.svg", "sql1.svg", "sql2.svg", "sql3.svg"]  # 输出的 SVG 文件
        for i in output_svg:
            os.rename(i, os.path.join(folder_name, i))
    print(f"Files and README.md have been moved to folder: {folder_name}")

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
