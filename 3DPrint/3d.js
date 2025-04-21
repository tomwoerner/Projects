// JS example
const loader = new THREE.STLLoader();
loader.load('/file.stl', function (geometry) {
  const material = new THREE.MeshStandardMaterial({ color: 0x888888 });
  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);
});
