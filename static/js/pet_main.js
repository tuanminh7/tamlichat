let scene, camera, renderer, petModel, mixer, controls;
let currentMood = 'happy';
let currentHealth = 100;
let currentLevel = 1;
let currentPetType = 'dragon';
let currentPetName = 'Pet';
let animationId;
let clock = new THREE.Clock();
let particles = [];
let weatherContainer;

const moodNames = {
    'happy': 'Vui Vẻ',
    'good': 'Khá Tốt',
    'worried': 'Lo Lắng',
    'tired': 'Mệt Mỏi',
    'sad': 'Buồn',
    'critical': 'Nguy Kịch'
};

const MODEL_PATHS = {
    dragon: {
        1: '/static/model/source/dragon_level1.glb',
        2: '/static/model/source/dragon_level2.glb',
        3: '/static/model/source/dragon_level3.glb',
        4: '/static/model/source/dragon_level4.glb'
    },
    pikachu: {
        1: '/static/model/source/pikachu_level1.glb',
        2: '/static/model/source/pikachu_level2.glb',
        3: '/static/model/source/pikachu_level3.glb',
        4: '/static/model/source/pikachu_level4.glb'
    },
    capybara: {
        1: '/static/model/source/capybara_level1.glb',
        2: '/static/model/source/capybara_level2.glb',
        3: '/static/model/source/capybara_level3.glb',
        4: '/static/model/source/capybara_level4.glb'
    }
};

function initThreeJS() {
    const canvas = document.getElementById('petCanvas');
    const container = canvas.parentElement;
    weatherContainer = document.getElementById('weatherEffects');

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f7fa);

    camera = new THREE.PerspectiveCamera(
        45,
        container.clientWidth / container.clientHeight,
        0.1,
        1000
    );
    camera.position.set(0, 2, 5);

    renderer = new THREE.WebGLRenderer({ 
        canvas: canvas, 
        antialias: true 
    });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1.5);
    directionalLight.position.set(5, 10, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.left = -10;
    directionalLight.shadow.camera.right = 10;
    directionalLight.shadow.camera.top = 10;
    directionalLight.shadow.camera.bottom = -10;
    scene.add(directionalLight);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight2.position.set(-5, 5, -5);
    scene.add(directionalLight2);

    const pointLight1 = new THREE.PointLight(0x667eea, 0.8);
    pointLight1.position.set(-5, 3, 0);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0x764ba2, 0.8);
    pointLight2.position.set(5, 3, 0);
    scene.add(pointLight2);

    const pointLight3 = new THREE.PointLight(0xffffff, 1.0);
    pointLight3.position.set(0, 5, 5);
    scene.add(pointLight3);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 3;
    controls.maxDistance = 10;
    controls.maxPolarAngle = Math.PI / 2;
    controls.target.set(0, 1, 0);
    controls.autoRotate = false;

    createParticleSystem();
    animate();
    window.addEventListener('resize', onWindowResize, false);
}

function loadPetModel(petType, level) {
    const modelPath = MODEL_PATHS[petType][level];
    
    if (petModel) {
        scene.remove(petModel);
        petModel = null;
        mixer = null;
    }

    const loader = new THREE.GLTFLoader();
    loader.load(
        modelPath,
        function(gltf) {
            petModel = gltf.scene;
            petModel.scale.set(1.5, 1.5, 1.5);
            petModel.position.set(0, 0, 0);

            petModel.traverse(function(child) {
                if (child.isMesh) {
                    child.castShadow = true;
                    child.receiveShadow = true;
                    
                    if (child.material) {
                        child.material.needsUpdate = true;
                        
                        if (!child.material.map) {
                            child.material.color.setHex(0xffffff);
                            child.material.metalness = 0.3;
                            child.material.roughness = 0.7;
                        }
                    }
                }
            });

            scene.add(petModel);

            if (gltf.animations && gltf.animations.length > 0) {
                mixer = new THREE.AnimationMixer(petModel);
                const action = mixer.clipAction(gltf.animations[0]);
                action.play();
            }
        },
        function(xhr) {
            console.log((xhr.loaded / xhr.total * 100) + '% loaded');
        },
        function(error) {
            console.error('Error loading model:', error);
        }
    );
}

function createParticleSystem() {
    const geometry = new THREE.BufferGeometry();
    const positions = [];
    const colors = [];

    for (let i = 0; i < 100; i++) {
        positions.push(
            Math.random() * 20 - 10,
            Math.random() * 20 - 10,
            Math.random() * 20 - 10
        );
        colors.push(1, 1, 1);
    }

    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
        size: 0.1,
        vertexColors: true,
        transparent: true,
        opacity: 0.8
    });

    const particleSystem = new THREE.Points(geometry, material);
    particles.push(particleSystem);
    scene.add(particleSystem);
}

function onWindowResize() {
    const container = document.getElementById('petCanvas').parentElement;
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    animationId = requestAnimationFrame(animate);

    const delta = clock.getDelta();
    const time = Date.now() * 0.001;

    if (mixer) {
        mixer.update(delta);
    }

    if (petModel) {
        updatePetAnimation(time);
    }

    if (particles.length > 0) {
        updateParticles(time);
    }

    controls.update();
    renderer.render(scene, camera);
}

function updatePetAnimation(time) {
    const targetScale = getScaleByHealth(currentHealth);
    petModel.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.05);

    if (currentMood === 'happy') {
        petModel.position.y = Math.sin(time * 3) * 0.8 + 0.5;
        petModel.rotation.z = Math.sin(time * 2) * 0.15;
        
        const radius = 2;
        petModel.position.x = Math.cos(time * 0.5) * radius;
        petModel.position.z = Math.sin(time * 0.5) * radius;
        petModel.rotation.y = time * 0.5 + Math.PI / 2;

    } else if (currentMood === 'good') {
        const walkRadius = 1.5;
        petModel.position.x = Math.cos(time * 0.8) * walkRadius;
        petModel.position.z = Math.sin(time * 0.8) * walkRadius;
        petModel.position.y = Math.sin(time * 4) * 0.15 + 0.2;
        petModel.rotation.y = time * 0.8 + Math.PI / 2;

    } else if (currentMood === 'worried') {
        petModel.position.x = Math.sin(time * 4) * 0.2;
        petModel.position.y = Math.sin(time * 3) * 0.15;
        petModel.position.z = Math.cos(time * 4) * 0.2;
        petModel.rotation.y = Math.sin(time * 2) * 0.3;
        petModel.rotation.z = Math.sin(time * 3) * 0.1;

    } else if (currentMood === 'tired') {
        petModel.position.y = Math.sin(time * 0.8) * 0.08 - 0.4;
        petModel.rotation.x = 0.3;
        petModel.rotation.z = Math.sin(time * 0.5) * 0.05;

    } else if (currentMood === 'sad') {
        petModel.position.y = -0.6;
        petModel.rotation.x = 0.5;
        petModel.rotation.z = Math.sin(time * 0.3) * 0.03;
        petModel.position.x = Math.sin(time * 0.5) * 0.05;

    } else if (currentMood === 'critical') {
        petModel.position.x = Math.sin(time * 8) * 0.4;
        petModel.position.y = Math.sin(time * 6) * 0.3 - 0.5;
        petModel.position.z = Math.cos(time * 7) * 0.3;
        petModel.rotation.x = Math.sin(time * 5) * 0.3 + 0.4;
        petModel.rotation.z = Math.sin(time * 9) * 0.4;
        
        camera.position.x += Math.sin(time * 10) * 0.02;
        camera.position.y += Math.cos(time * 10) * 0.02;
    }
}

function updateParticles(time) {
    particles.forEach(particle => {
        const positions = particle.geometry.attributes.position.array;
        for (let i = 0; i < positions.length; i += 3) {
            positions[i + 1] += Math.sin(time + i) * 0.01;
        }
        particle.geometry.attributes.position.needsUpdate = true;
    });
}

function getScaleByHealth(health) {
    if (health >= 90) return 2.0;
    if (health >= 70) return 1.7;
    if (health >= 50) return 1.4;
    if (health >= 30) return 1.1;
    if (health >= 15) return 0.8;
    return 0.6;
}

function updatePetMood(mood, health) {
    currentMood = mood;
    currentHealth = health;

    if (!petModel) return;

    const moodColors = {
        'happy': 0xffd89b,
        'good': 0xa8edea,
        'worried': 0xfdcbf1,
        'tired': 0xd299c2,
        'sad': 0x9890e3,
        'critical': 0x757f9a
    };

    const color = moodColors[mood] || 0xffffff;

    petModel.traverse(function(child) {
        if (child.isMesh) {
            if (child.material) {
                child.material.emissive = new THREE.Color(color);
                child.material.emissiveIntensity = 0.3;
            }
        }
    });

    scene.background = new THREE.Color(color).lerp(new THREE.Color(0xffffff), 0.8);

    updateWeatherEffects(mood);
}

function updateWeatherEffects(mood) {
    weatherContainer.innerHTML = '';

    if (mood === 'happy') {
        createSunEffect();
        createHeartEffect();
        createGlitterEffect();
    } else if (mood === 'good') {
        createStarEffect();
        createSnowEffect();
    } else if (mood === 'worried') {
        createCloudEffect();
    } else if (mood === 'tired') {
        createCloudEffect();
        createRainEffect();
    } else if (mood === 'sad') {
        createRainEffect();
        createCloudEffect();
    } else if (mood === 'critical') {
        createRainEffect();
        createStormEffect();
    }
}

function createSunEffect() {
    const sun = document.createElement('div');
    sun.style.position = 'absolute';
    sun.style.top = '30px';
    sun.style.right = '30px';
    sun.style.width = '80px';
    sun.style.height = '80px';
    sun.style.borderRadius = '50%';
    sun.style.background = 'radial-gradient(circle, #ffd700, #ffa500)';
    sun.style.boxShadow = '0 0 40px #ffd700';
    weatherContainer.appendChild(sun);

    for (let i = 0; i < 12; i++) {
        const ray = document.createElement('div');
        ray.className = 'sun-ray';
        ray.style.left = '50%';
        ray.style.top = '30px';
        ray.style.transform = `rotate(${i * 30}deg)`;
        ray.style.animationDelay = `${i * 0.1}s`;
        weatherContainer.appendChild(ray);
    }
}

function createHeartEffect() {
    setInterval(() => {
        const heart = document.createElement('div');
        heart.className = 'heart';
        heart.style.left = Math.random() * 100 + '%';
        heart.style.bottom = '0';
        weatherContainer.appendChild(heart);

        setTimeout(() => heart.remove(), 2000);
    }, 800);
}

function createGlitterEffect() {
    setInterval(() => {
        const glitter = document.createElement('div');
        glitter.className = 'glitter';
        glitter.style.left = Math.random() * 100 + '%';
        glitter.style.top = Math.random() * 100 + '%';
        weatherContainer.appendChild(glitter);

        setTimeout(() => glitter.remove(), 1000);
    }, 300);
}

function createStarEffect() {
    for (let i = 0; i < 20; i++) {
        setTimeout(() => {
            const star = document.createElement('div');
            star.className = 'star';
            star.style.left = Math.random() * 100 + '%';
            star.style.top = Math.random() * 100 + '%';
            star.style.animationDelay = Math.random() * 2 + 's';
            weatherContainer.appendChild(star);
        }, i * 100);
    }
}

function createSnowEffect() {
    setInterval(() => {
        const snow = document.createElement('div');
        snow.className = 'snowflake';
        snow.style.left = Math.random() * 100 + '%';
        snow.style.top = '-10px';
        snow.style.animationDuration = (Math.random() * 2 + 2) + 's';
        snow.style.animationDelay = Math.random() * 2 + 's';
        weatherContainer.appendChild(snow);

        setTimeout(() => snow.remove(), 5000);
    }, 300);
}

function createCloudEffect() {
    for (let i = 0; i < 3; i++) {
        const cloud = document.createElement('div');
        cloud.className = 'cloud';
        cloud.style.top = (Math.random() * 30 + 10) + '%';
        cloud.style.left = '-100px';
        cloud.style.animationDuration = (Math.random() * 5 + 8) + 's';
        cloud.style.animationDelay = i + 's';
        weatherContainer.appendChild(cloud);
    }
}

function createRainEffect() {
    setInterval(() => {
        const rain = document.createElement('div');
        rain.className = 'rain';
        rain.style.left = Math.random() * 100 + '%';
        rain.style.top = '-20px';
        rain.style.animationDuration = (Math.random() * 0.5 + 0.8) + 's';
        weatherContainer.appendChild(rain);

        setTimeout(() => rain.remove(), 2000);
    }, 100);
}

function createStormEffect() {
    setInterval(() => {
        weatherContainer.style.background = 'rgba(255, 0, 0, 0.1)';
        setTimeout(() => {
            weatherContainer.style.background = 'transparent';
        }, 100);
    }, 500);
}

async function loadPetStatus() {
    try {
        const response = await fetch('/student/pet/status');
        const data = await response.json();

        if (data.error && data.redirect) {
            window.location.href = data.redirect;
            return;
        }

        currentPetType = data.pet_type;
        currentPetName = data.pet_name;
        currentLevel = data.level;

        if (!petModel || currentLevel !== data.level) {
            loadPetModel(currentPetType, currentLevel);
        }

        document.getElementById('healthValue').textContent = data.health + '%';
        document.getElementById('healthFill').style.width = data.health + '%';
        
        if (data.health >= 70) {
            document.getElementById('healthFill').className = 'health-fill health-high';
        } else if (data.health >= 40) {
            document.getElementById('healthFill').className = 'health-fill health-medium';
        } else {
            document.getElementById('healthFill').className = 'health-fill health-low';
        }

        updatePetMood(data.mood, data.health);

        document.getElementById('moodDescription').innerHTML = '<p>' + data.mood_description + '</p>';
        document.getElementById('totalCare').textContent = data.total_care_count;
        document.getElementById('currentMood').textContent = moodNames[data.mood] || data.mood;
        document.getElementById('petNameDisplay').textContent = data.pet_name;
        document.getElementById('petLevel').textContent = 'Level ' + data.level;

        updateLevelProgress(data.level_progress);
        checkLevelNotification();

    } catch (error) {
        console.error('Lỗi khi tải trạng thái pet:', error);
    }
}

function updateLevelProgress(progress) {
    const progressSection = document.getElementById('levelProgressSection');
    
    if (progress.is_max_level) {
        progressSection.innerHTML = `
            <div class="max-level-badge">
                <div class="badge-icon">👑</div>
                <div class="badge-text">ĐÃ ĐẠT MAX LEVEL!</div>
            </div>
        `;
        return;
    }

    progressSection.innerHTML = `
        <div class="progress-title">Tiến Độ Lên Level ${progress.next_level}</div>
        
        <div class="progress-item">
            <div class="progress-label">
                <span>Ngày Đạt 100 HP</span>
                <span>${progress.days_current}/${progress.days_needed} ngày</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress.days_progress}%"></div>
            </div>
        </div>

        <div class="progress-item">
            <div class="progress-label">
                <span>Số Lần Chat</span>
                <span>${progress.chats_current}/${progress.chats_needed} lần</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${progress.chats_progress}%"></div>
            </div>
        </div>
    `;
}

async function checkLevelNotification() {
    try {
        const response = await fetch('/student/pet/level-notification');
        const data = await response.json();

        if (data.has_notification) {
            showLevelUpNotification(data.message, data.new_level);
        }
    } catch (error) {
        console.error('Lỗi khi kiểm tra thông báo:', error);
    }
}

function showLevelUpNotification(message, newLevel) {
    const overlay = document.createElement('div');
    overlay.className = 'level-up-overlay';
    overlay.innerHTML = `
        <div class="level-up-card">
            <div class="level-up-icon">🎉</div>
            <h2>${message}</h2>
            <div class="level-badge">LEVEL ${newLevel}</div>
            <button onclick="this.parentElement.parentElement.remove()" class="close-notification">
                Tuyệt Vời!
            </button>
        </div>
    `;
    document.body.appendChild(overlay);
}

async function loadTasks() {
    try {
        const response = await fetch('/student/tasks/available');
        const data = await response.json();

        const tasksContainer = document.getElementById('tasksList');
        tasksContainer.innerHTML = '';
        tasksContainer.className = '';

        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'task-category';
        categoryDiv.innerHTML = '<div class="category-title">Nhiệm Vụ Được Đề Xuất</div>';
        
        const taskList = document.createElement('div');
        taskList.className = 'task-list';

        data.suggested_tasks.forEach(task => {
            const taskItem = document.createElement('div');
            taskItem.className = 'task-item';
            taskItem.innerHTML = `
                <div class="task-info">
                    <div class="task-name">${task.name}</div>
                    <div class="task-meta">+${task.health_bonus} sức khỏe | ${task.duration}</div>
                </div>
                <button class="task-button" onclick="completeTask('${task.id}', '${task.name}', ${task.health_bonus})">
                    Hoàn Thành
                </button>
            `;
            taskList.appendChild(taskItem);
        });

        categoryDiv.appendChild(taskList);
        tasksContainer.appendChild(categoryDiv);

    } catch (error) {
        console.error('Lỗi khi tải nhiệm vụ:', error);
        document.getElementById('tasksList').innerHTML = '<p>Không thể tải nhiệm vụ</p>';
    }
}

async function completeTask(taskId, taskName, healthBonus) {
    try {
        const response = await fetch('/student/tasks/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                task_id: taskId,
                task_name: taskName,
                health_bonus: healthBonus
            })
        });

        const data = await response.json();

        if (data.success) {
            showSuccessMessage(data.message);
            await loadPetStatus();
            await loadTasks();
            await loadHistory();
        }

    } catch (error) {
        console.error('Lỗi khi hoàn thành nhiệm vụ:', error);
        alert('Có lỗi xảy ra khi hoàn thành nhiệm vụ');
    }
}

async function loadHistory() {
    try {
        const response = await fetch('/student/tasks/history');
        const data = await response.json();

        const historyContainer = document.getElementById('historyList');
        historyContainer.innerHTML = '';
        historyContainer.className = 'history-list';

        if (data.history.length === 0) {
            historyContainer.innerHTML = '<p>Chưa có lịch sử chăm sóc</p>';
            historyContainer.className = 'loading';
            return;
        }

        data.history.reverse().forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            
            const date = new Date(item.completed_at);
            const timeStr = date.toLocaleString('vi-VN');

            historyItem.innerHTML = `
                <div class="task-name">${item.task_name}</div>
                <div class="task-time">${timeStr}</div>
                <div class="task-bonus">+${item.health_bonus} sức khỏe</div>
            `;
            historyContainer.appendChild(historyItem);
        });

    } catch (error) {
        console.error('Lỗi khi tải lịch sử:', error);
        document.getElementById('historyList').innerHTML = '<p>Không thể tải lịch sử</p>';
    }
}

function showSuccessMessage(message) {
    const msgDiv = document.getElementById('successMessage');
    msgDiv.textContent = message;
    msgDiv.style.display = 'block';

    setTimeout(() => {
        msgDiv.style.display = 'none';
    }, 3000);
}

window.addEventListener('load', function() {
    initThreeJS();
    loadPetStatus();
    loadTasks();
    loadHistory();

    setInterval(loadPetStatus, 30000);
});