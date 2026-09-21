#!/usr/bin/env python3
"""
Version 6 (Advanced PHY) - Step 4: Multi-Target Tracking & Kalman Filtering
-------------------------------------------------------------------------------------
Ingests OS-CFAR detections across consecutive frame intervals, performs Global
Nearest Neighbor (GNN) data association via Mahalanobis gating, and maintains
linear Kalman Filter (KF) state estimates for active tracks.

Author: Abhishek Singh
Repository: 6g-chaotic-superposition-phy
License: MIT
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linear_sum_assignment

# =====================================================================
# Tracking Parameters
# =====================================================================
FRAME_INTERVAL = 0.05          # Time step between radar frames (dt = 50 ms)
NUM_FRAMES = 20                # Simulation horizon (1 second)
GATING_THRESHOLD = 9.21        # Chi-Square 99% confidence boundary for 2D gating

# Process & Measurement Noise Covariances
Q_PROCESS = np.diag([0.1, 0.5])**2    # Motion model uncertainty (Range std=0.1m, Vel std=0.5m/s)
R_MEAS = np.diag([0.2, 1.0])**2       # OS-CFAR measurement error (Range std=0.2m, Vel std=1.0m/s)

# =====================================================================
# Kalman Filter Track Class
# =====================================================================
class TargetTrack:
    _track_id_counter = 1

    def __init__(self, init_range, init_velocity, dt=FRAME_INTERVAL):
        self.track_id = TargetTrack._track_id_counter
        TargetTrack._track_id_counter += 1
        
        self.dt = dt
        # State vector [Range, Velocity]^T
        self.x = np.array([[init_range], [init_velocity / 3.6]])  # Velocity internal in m/s
        
        # State Covariance Matrix
        self.P = np.diag([1.0, 5.0])**2
        
        # State Transition Matrix (CV Model)
        self.F = np.array([
            [1.0, self.dt],
            [0.0, 1.0]
        ])
        
        # Measurement Matrix
        self.H = np.eye(2)
        
        self.hits = 1
        self.misses = 0
        self.history = []

    def predict(self):
        """Predicts target state and covariance for next time step."""
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + Q_PROCESS
        return self.x

    def update(self, z_meas):
        """Updates target state with associated measurement z = [range, velocity_ms]^T."""
        y = z_meas - self.H @ self.x              # Measurement residual (innovation)
        S = self.H @ self.P @ self.H.T + R_MEAS    # Innovation covariance
        K = self.P @ self.H.T @ np.linalg.inv(S)   # Kalman Gain
        
        self.x = self.x + K @ y
        self.P = (np.eye(2) - K @ self.H) @ self.P
        
        self.hits += 1
        self.misses = 0
        self.history.append((self.x[0, 0], self.x[1, 0] * 3.6))

    def mahalanobis_distance(self, z_meas):
        """Calculates Mahalanobis distance metric for data association gating."""
        y = z_meas - self.H @ self.x
        S = self.H @ self.P @ self.H.T + R_MEAS
        return float(y.T @ np.linalg.inv(S) @ y)

# =====================================================================
# Target Tracker Core (GNN Association Engine)
# =====================================================================
class ISACMultiTargetTracker:
    def __init__(self):
        self.tracks = []

    def process_frame(self, detections):
        """
        Processes OS-CFAR detections for current frame.
        detections: list of tuples [(range_m, velocity_kmh), ...]
        """
        # Convert measurements to internal SI units [m, m/s]
        meas_vectors = [np.array([[d[0]], [d[1] / 3.6]]) for d in detections]
        
        # 1. Predict state for all active tracks
        for track in self.tracks:
            track.predict()
            
        if len(self.tracks) == 0:
            for z in meas_vectors:
                self.tracks.append(TargetTrack(z[0, 0], z[1, 0] * 3.6))
            return

        # 2. Build Cost Matrix for GNN Data Association
        num_tracks = len(self.tracks)
        num_meas = len(meas_vectors)
        cost_matrix = np.full((num_tracks, num_meas), 1e6)
        
        for t_idx, track in enumerate(self.tracks):
            for m_idx, z in enumerate(meas_vectors):
                dist = track.mahalanobis_distance(z)
                if dist < GATING_THRESHOLD:
                    cost_matrix[t_idx, m_idx] = dist

        # 3. Hungarian Algorithm Optimization for Global Nearest Neighbor
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        assigned_tracks = set()
        assigned_meas = set()
        
        for r, c in zip(row_ind, col_ind):
            if cost_matrix[r, c] < GATING_THRESHOLD:
                self.tracks[r].update(meas_vectors[c])
                assigned_tracks.add(r)
                assigned_meas.add(c)
                
        # Handle unassigned tracks
        for t_idx, track in enumerate(self.tracks):
            if t_idx not in assigned_tracks:
                track.misses += 1
                
        # Initialize new tracks for unassigned measurements
        for m_idx in range(num_meas):
            if m_idx not in assigned_meas:
                z = meas_vectors[m_idx]
                self.tracks.append(TargetTrack(z[0, 0], z[1, 0] * 3.6))
                
        # Prune dead tracks (missed > 3 consecutive frames)
        self.tracks = [t for t in self.tracks if t.misses <= 3]

# =====================================================================
# Main Execution Pipeline
# =====================================================================
def run_target_tracking():
    print("=" * 70)
    print("--- Step 4: Multi-Target Trajectory Tracking & Kalman Filtering ---")
    print("=" * 70)
    
    tracker = ISACMultiTargetTracker()
    
    # Ground truth initial states
    gt_targets = [
        {"range": 12.5, "velocity": 45.0},
        {"range": 28.0, "velocity": -80.0},
        {"range": 13.2, "velocity": 48.0}
    ]
    
    track_logs = {1: [], 2: [], 3: []}
    time_grid = np.arange(NUM_FRAMES) * FRAME_INTERVAL
    
    np.random.seed(42)
    for frame_idx in range(NUM_FRAMES):
        t = time_grid[frame_idx]
        frame_detections = []
        
        # Simulate noisy OS-CFAR detections across time
        for tgt in gt_targets:
            # Kinematic position update
            current_r = tgt["range"] + (tgt["velocity"] / 3.6) * t
            current_v = tgt["velocity"]
            
            # Add measurement noise
            meas_r = current_r + np.random.normal(0, 0.15)
            meas_v = current_v + np.random.normal(0, 0.8)
            frame_detections.append((meas_r, meas_v))
            
        tracker.process_frame(frame_detections)
        
        for trk in tracker.tracks:
            if trk.track_id in track_logs:
                track_logs[trk.track_id].append((t, trk.x[0, 0], trk.x[1, 0] * 3.6))
                
    print(f"Total Active Tracks Maintained: {len(tracker.tracks)}")
    print("-" * 70)
    print("Final State Estimates at t = 1.0s:")
    for trk in tracker.tracks:
        print(f" Track #{trk.track_id}: Estimated Range = {trk.x[0,0]:.2f} m | Velocity = {trk.x[1,0]*3.6:.2f} km/h")
    print("=" * 70)

    # Visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    colors = ['r', 'g', 'b']
    for trk_id, log in track_logs.items():
        if len(log) > 0:
            log_arr = np.array(log)
            ax1.plot(log_arr[:, 0], log_arr[:, 1], f'{colors[trk_id-1]}o-', label=f'Track #{trk_id} Range')
            ax2.plot(log_arr[:, 0], log_arr[:, 2], f'{colors[trk_id-1]}s--', label=f'Track #{trk_id} Velocity')
            
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Range (m)')
    ax1.set_title('Target Range Trajectories vs Time')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend()
    
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Velocity (km/h)')
    ax2.set_title('Target Velocity Trajectories vs Time')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend()
    
    os.makedirs('docs/images', exist_ok=True)
    plt.tight_layout()
    plt.savefig('docs/images/isac_target_tracking.png', dpi=300)
    print("[SUCCESS] Tracking output plot saved to 'docs/images/isac_target_tracking.png'.")

if __name__ == '__main__':
    run_target_tracking()
