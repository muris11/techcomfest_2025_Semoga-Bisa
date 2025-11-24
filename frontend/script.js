const API_BASE = "http://localhost:5000";
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
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;

  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        username: email,
        password: password,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      token = data.access_token;
      localStorage.setItem("token", token);
      showDashboard();
    } else {
      alert("Login failed");
    }
  } catch (error) {
    console.error("Login error:", error);
    alert("Login error");
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById("reg-name").value;
  const email = document.getElementById("reg-email").value;
  const password = document.getElementById("reg-password").value;
  const domicile = document.getElementById("reg-domicile").value;

  try {
    const response = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        name,
        email,
        password,
        domicile,
      }),
    });

    if (response.ok) {
      alert("Registration successful! Please login.");
      showLogin();
    } else {
      const error = await response.json();
      alert(`Registration failed: ${error.detail}`);
    }
  } catch (error) {
    console.error("Register error:", error);
    alert("Registration error");
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
      alert("Scan failed");
    }
  } catch (error) {
    console.error("Scan error:", error);
    alert("Scan error");
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
      const error = await response.json();
      alert(`Deposit failed: ${error.detail}`);
    }
  } catch (error) {
    console.error("Deposit error:", error);
    alert("Deposit error");
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
    }
  } catch (error) {
    console.error("Load deposits error:", error);
  }
}
