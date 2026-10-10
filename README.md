# ⚡ NetPulse — Internet Usage Monitor

\<p align="center">
&#x20; \<strong>Monitor your network. Understand your usage.\</strong>
\</p>

\<p align="center">
&#x20; A lightweight network monitoring dashboard built with Python and modern web technologies.
\</p>

---

## 🌐 About NetPulse

**NetPulse** is a desktop-oriented internet usage monitoring application designed to help users understand their network activity through a clean, intuitive dashboard.

It provides real-time download and upload statistics, tracks daily and monthly data consumption, stores historical usage locally, and delivers desktop notifications to keep users informed about their internet activity.

Whether you want to monitor your connection, analyze your data consumption, or keep track of your daily network usage, NetPulse brings essential network statistics together in one place.

## ✨ Features

- 📡 **Real-Time Network Monitoring** — Track download and upload speeds.
- 📊 **Usage Analytics** — Review daily and monthly data consumption.
- 🕒 **Historical Statistics** — Explore hourly and daily network usage.
- 🔔 **Desktop Notifications** — Receive periodic summaries of your network activity.
- 🖥️ **Network Interface Selection** — Monitor a selected network adapter.
- 💾 **Local Data Storage** — Save usage statistics with SQLite.
- 🔒 **Local-First Design** — No cloud database or user account required for local monitoring.
- ⚙️ **Python-Based Backend** — Built with lightweight, widely used technologies.

## 🛠️ Built With

| Technology         | Purpose                                |
| ------------------ | -------------------------------------- |
| Python             | Core application logic                 |
| Flask              | Local web server and API               |
| psutil             | System and network statistics          |
| SQLite             | Local data storage                     |
| Plyer              | Desktop notifications                  |
| React & TypeScript | Frontend source code                   |
| Vite               | Frontend development and build tooling |

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or newer
- pip
- Node.js and npm, if building the React frontend separately

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/amiraliad06-cpu/NetPulse-Internet-Usage-Monitor
cd NetPulse-Internet-Usage-Monitor
```

**2. Create a virtual environment**

```bash
python -m venv .venv
```

**3. Activate the environment**

Windows:

```bat
.venv\Scripts\activate
```

Linux / macOS:

```bash
source .venv/bin/activate
```

**4. Install dependencies**

```bash
python -m pip install -r requirements.txt
```

**5. Run the application**

```bash
python app.py
```

**6. Open the dashboard**

Visit:

```text
http://127.0.0.1:5000
```

Keep the terminal open while using the application.

## 💾 Data & Privacy

NetPulse is designed for local monitoring. Usage statistics can be stored in an SQLite database on the user's computer.

The application does not require a cloud database or an online account for its local monitoring workflow. Network statistics are collected from the operating system and may vary from the usage figures reported by an internet service provider.

## 🗺️ Roadmap

Potential future improvements include:

- [ ] Export usage reports to CSV
- [ ] Configurable data usage limits
- [ ] Custom notification thresholds
- [ ] Improved network adapter detection
- [ ] Application-level traffic analysis
- [ ] Enhanced dashboard visualizations
- [ ] Standalone desktop installer
- [ ] Additional language support

## ⚠️ Limitations

- Monitoring accuracy depends on operating system network counters.
- The application does not inherently identify the traffic usage of every individual program.
- The local server must remain running for live monitoring.
- The React frontend may require a separate build process, depending on the project configuration.

## 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

If you find a bug or have an idea for improvement, feel free to open an issue or submit a pull request.

## 📄 License

A license has not yet been specified. Please add a license file before distributing the project for reuse or modification.

---

\<p align="center">
&#x20; \<strong>NetPulse\</strong>\<br>
&#x20; \<em>See your network. Track your data. Stay informed.\</em>
\</p>
