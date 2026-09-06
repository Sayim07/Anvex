// CyberGlobe3D.jsx — Interactive 3D Cyber Wireframe Globe using Three.js
import { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function CyberGlobe3D({ size = 120 }) {
  const mountRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    // Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 1000);
    camera.position.z = 180;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(size, size);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Group to hold all 3D cyber elements
    const globeGroup = new THREE.Group();
    scene.add(globeGroup);

    // 1. Inner Wireframe Sphere
    const sphereGeo = new THREE.SphereGeometry(45, 18, 14);
    const sphereMat = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      wireframe: true,
      transparent: true,
      opacity: 0.35,
    });
    const globe = new THREE.Mesh(sphereGeo, sphereMat);
    globeGroup.add(globe);

    // 2. Core glowing nucleus
    const coreGeo = new THREE.IcosahedronGeometry(22, 1);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0x38bdf8,
      wireframe: true,
      transparent: true,
      opacity: 0.55,
    });
    const core = new THREE.Mesh(coreGeo, coreMat);
    globeGroup.add(core);

    // 3. Orbital Data Rings
    const ringGeo1 = new THREE.RingGeometry(55, 57, 48);
    const ringMat1 = new THREE.MeshBasicMaterial({
      color: 0x818cf8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.45,
    });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    globeGroup.add(ring1);

    const ringGeo2 = new THREE.RingGeometry(62, 63.5, 48);
    const ringMat2 = new THREE.MeshBasicMaterial({
      color: 0x00f0ff,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.3,
    });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.y = Math.PI / 4;
    globeGroup.add(ring2);

    // 4. Data Nodes / Particle Cloud
    const particleCount = 60;
    const posArray = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      const u = Math.random();
      const v = Math.random();
      const theta = u * 2.0 * Math.PI;
      const phi = Math.acos(2.0 * v - 1.0);
      const r = 48 + Math.random() * 12;
      posArray[i] = r * Math.sin(phi) * Math.cos(theta);
      posArray[i + 1] = r * Math.sin(phi) * Math.sin(theta);
      posArray[i + 2] = r * Math.cos(phi);
    }

    const particlesGeo = new THREE.BufferGeometry();
    particlesGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
    const particlesMat = new THREE.PointsMaterial({
      size: 2.2,
      color: 0x38bdf8,
      transparent: true,
      opacity: 0.85,
    });
    const particleSystem = new THREE.Points(particlesGeo, particlesMat);
    globeGroup.add(particleSystem);

    // Mouse Interaction
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    const handleMouseMove = (e) => {
      const rect = container.getBoundingClientRect();
      const x = e.clientX - (rect.left + rect.width / 2);
      const y = e.clientY - (rect.top + rect.height / 2);
      targetX = (x / rect.width) * 0.8;
      targetY = (y / rect.height) * 0.8;
    };

    window.addEventListener('mousemove', handleMouseMove);

    // Animation Loop
    let reqId;
    const clock = new THREE.Clock();

    const animate = () => {
      reqId = requestAnimationFrame(animate);
      const delta = clock.getDelta();

      // Smooth mouse lerp
      mouseX += (targetX - mouseX) * 0.05;
      mouseY += (targetY - mouseY) * 0.05;

      // Base rotation
      globe.rotation.y += 0.4 * delta;
      core.rotation.y -= 0.6 * delta;
      ring1.rotation.z += 0.3 * delta;
      ring2.rotation.x += 0.25 * delta;
      particleSystem.rotation.y += 0.2 * delta;

      // React to mouse
      globeGroup.rotation.y = mouseX + globe.rotation.y;
      globeGroup.rotation.x = mouseY;

      renderer.render(scene, camera);
    };

    animate();

    return () => {
      cancelAnimationFrame(reqId);
      window.removeEventListener('mousemove', handleMouseMove);
      if (container && renderer.domElement) {
        container.removeChild(renderer.domElement);
      }
      sphereGeo.dispose();
      sphereMat.dispose();
      coreGeo.dispose();
      coreMat.dispose();
      ringGeo1.dispose();
      ringMat1.dispose();
      ringGeo2.dispose();
      ringMat2.dispose();
      particlesGeo.dispose();
      particlesMat.dispose();
      renderer.dispose();
    };
  }, [size]);

  return (
    <div 
      ref={mountRef} 
      className="relative flex items-center justify-center cursor-pointer select-none"
      style={{ width: size, height: size }}
      title="Interactive 3D Threat Radar Node — Move mouse to orient"
    />
  );
}
