// Tentukan base URL API backend.
// - Jika frontend dibuka lewat Live Server (port 5500),
//   arahkan ke backend FastAPI di port 8000.
// - Jika dibuka dari FastAPI sendiri (port 8000, path /frontend/...),
//   gunakan origin yang sama (string kosong).
const API_BASE =
  window.location.port === "5500"
    ? "http://127.0.0.1:8000"
    : "";
console.log("API_BASE =", API_BASE);
let token = localStorage.getItem("token");

document.addEventListener("DOMContentLoaded", () => {
  if (token) {
    showDashboard();
  } else {
    showAuth();
  }

  // Event listeners
  document
    .getElementById("login-btn")
    .addEventListener("click", () => showLogin());
  document
    .getElementById("register-btn")
    .addEventListener("click", () => showRegister());
  document.getElementById("login").addEventListener("submit", handleLogin);
  document
    .getElementById("register")
    .addEventListener("submit", handleRegister);
  document
    .getElementById("google-login")
    .addEventListener("click", handleGoogleLogin);
  document.getElementById("scan-btn").addEventListener("click", handleScan);
  document.getElementById("deposit").addEventListener("submit", handleDeposit);
  document.getElementById("logout-btn").addEventListener("click", handleLogout);
});

function showAuth() {
  document.getElementById("auth-section").classList.remove("hidden");
  document.getElementById("dashboard").classList.add("hidden");
}

function showDashboard() {
  document.getElementById("auth-section").classList.add("hidden");
  document.getElementById("dashboard").classList.remove("hidden");
  loadUserInfo();
  loadDeposits();
}

function showLogin() {
  document.getElementById("login-form").classList.remove("hidden");
  document.getElementById("register-form").classList.add("hidden");
}

function showRegister() {
  document.getElementById("register-form").classList.remove("hidden");
  document.getElementById("login-form").classList.add("hidden");
}

async function handleLogin(e) {
  e.preventDefault();
  console.log('handleLogin called');
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  console.log('Email:', email, 'Password length:', password.length);

  try {
        console.log('Sending login request');
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username: email,
                password: password,
            }),
        });
        console.log('Response status:', response.status);

        if (response.ok) {
            const data = await response.json();
            console.log('Login successful, token:', data.access_token.substring(0, 10) + '...');
            token = data.access_token;
            localStorage.setItem('token', token);
            showDashboard();
        } else {
            const error = await response.json();
            console.log('Login failed, error:', error);
            alert(`Login failed: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Login error: ' + error.message);
    }
}

async function handleRegister(e) {
  e.preventDefault();
  console.log('handleRegister called');
  const name = document.getElementById('reg-name').value;
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;
  const domicile = document.getElementById('reg-domicile').value;
  console.log('Register data:', { name, email, passwordLength: password.length, domicile });

  try {
        console.log('Sending register request');
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                email,
                password,
                domicile,
            }),
        });
        console.log('Register response status:', response.status);

        if (response.ok) {
            console.log('Registration successful');
            alert('Registration successful! Please login.');
            showLogin();
        } else {
            const error = await response.json();
            console.log('Registration failed, error:', error);
            alert(`Registration failed: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Register error:', error);
        alert('Registration error: ' + error.message);
    }
}

async function handleGoogleLogin() {
  // For simplicity, simulate Google login
  alert("Google login not implemented in frontend. Use API directly.");
}

async function handleScan() {
  const fileInput = document.getElementById("waste-file");
  const file = fileInput.files[0];
  if (!file) {
    alert("Please select a file");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch(`${API_BASE}/waste/scan`, {
      method: "POST",
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      document.getElementById("scan-result").innerHTML = `
                <p>Waste Name: ${data.waste_name}</p>
                <p>Category: ${data.category}</p>
                <p>Info: ${data.info}</p>
            `;
    } else {
      let message = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        if (error && (error.detail || error.message)) {
          message = error.detail || error.message;
        }
      } catch {
        // respons bukan JSON, biarkan message default
      }
      alert(`Scan failed: ${message}`);
    }
  } catch (error) {
    console.error("Scan error:", error);
    alert("Scan error: " + error.message);
  }
}

async function handleDeposit(e) {
  e.preventDefault();
  const wasteName = document.getElementById("waste-name").value;
  const category = document.getElementById("category").value;
  const amount = parseFloat(document.getElementById("amount").value);
  const via = document.getElementById("via").value;

  try {
    const response = await fetch(`${API_BASE}/waste/deposits`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        waste_name: wasteName,
        category,
        amount,
        via,
      }),
    });

    if (response.ok) {
      alert("Deposit successful!");
      loadDeposits();
      loadUserInfo();
    } else {
      let message = `HTTP ${response.status}`;
      try {
        const error = await response.json();
        if (error && (error.detail || error.message)) {
          message = error.detail || error.message;
        }
      } catch {
        // respons bukan JSON, biarkan message default
      }
      alert(`Deposit failed: ${message}`);
    }
  } catch (error) {
    console.error("Deposit error:", error);
    alert("Deposit error: " + error.message);
  }
}

function handleLogout() {
  token = null;
  localStorage.removeItem("token");
  showAuth();
}

async function loadUserInfo() {
  try {
    const response = await fetch(`${API_BASE}/users/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const user = await response.json();
      document.getElementById("user-info").innerHTML = `
                <h3>Welcome, ${user.name}!</h3>
                <p>Email: ${user.email}</p>
                <p>Level: ${user.level}</p>
                <p>Total Points: ${user.total_points}</p>
                <p>Total Waste: ${user.total_waste_amount} kg</p>
            `;
    } else {
      console.error("Failed to load user info");
      // Perhaps redirect to login if unauthorized
      if (response.status === 401) {
        handleLogout();
      }
    }
  } catch (error) {
    console.error("Load user info error:", error);
  }
}

async function loadDeposits() {
  try {
    const response = await fetch(`${API_BASE}/waste/deposits`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.ok) {
      const deposits = await response.json();
      const depositsDiv = document.getElementById("deposits");
      depositsDiv.innerHTML = deposits
        .map(
          (deposit) => `
                <div class="deposit-item">
                    <p>Date: ${deposit.date}</p>
                    <p>Waste: ${deposit.waste_name}</p>
                    <p>Category: ${deposit.category}</p>
                    <p>Amount: ${deposit.amount} kg</p>
                    <p>Points: ${deposit.points_earned}</p>
                </div>
            `
        )
        .join("");
    } else {
      console.error("Failed to load deposits");
      if (response.status === 401) {
        handleLogout();
      }
    }
  } catch (error) {
    console.error("Load deposits error:", error);
  }
}
