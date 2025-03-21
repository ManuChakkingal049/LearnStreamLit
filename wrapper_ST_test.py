import streamlit as st

# Wrapper function
def stress_test_wrapper():
    st.title('Stress Test Dashboard')

    # List of stress tests
    tests = {
        'ST1 Stress Test': {
            'description': 'ST1 is a comprehensive stress test designed to assess the performance of your system under intense load conditions.',
            'link': 'https://learnapp-lpimbb9upxwnypyotzgt7j.streamlit.app/',  # Link to your ST1 app
        },
        'CPU Stress Test': {
            'description': 'This test will push the CPU to its maximum capacity to check for stability.',
            'link': 'http://localhost:8501/cpu_stress_test',  # Replace with your actual link
        },
        'Memory Stress Test': {
            'description': 'This test will allocate and deallocate memory to check for any leaks or issues.',
            'link': 'http://localhost:8501/memory_stress_test',  # Replace with your actual link
        },
        'Disk I/O Stress Test': {
            'description': 'This test will perform intensive disk read/write operations to check for bottlenecks.',
            'link': 'http://localhost:8501/disk_stress_test',  # Replace with your actual link
        },
        'Network Stress Test': {
            'description': 'This test will simulate heavy network traffic to check for performance under load.',
            'link': 'http://localhost:8501/network_stress_test',  # Replace with your actual link
        },
    }

    # Displaying buttons for each test and explanations
    for test_name, test_info in tests.items():
        if st.button(test_name):
            st.write(f"### {test_name}")
            st.write(test_info['description'])
            st.write(f"Click [here]({test_info['link']}) to access the full Streamlit app for this stress test.")

if __name__ == '__main__':
    stress_test_wrapper()
