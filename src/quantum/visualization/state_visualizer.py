#!/usr/bin/env python
"""
Copyright (c) 2025 nego-drama project contributors
All rights reserved.

This source code is licensed under the terms of the LICENSE file found in the
root directory of this source tree.
"""


# -*- coding: utf-8 -*-

"""
Quantum State Visualizer with GitHub Octocat theme.
Provides visualizations for quantum states, circuits, and entanglement.
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
import logging
import io
import base64
from enum import Enum

try:
    from qiskit import QuantumCircuit
    from qiskit.visualization import plot_bloch_multivector, plot_histogram, plot_state_city, plot_state_qsphere
    from qiskit.visualization.bloch import Bloch
    from qiskit.quantum_info import Statevector, DensityMatrix
except ImportError:
    logging.warning("Qiskit not installed. Limited visualization functionality available.")


class VisualizationStyle(Enum):
    """Enumeration of visualization styles."""
    STANDARD = "standard"
    GITHUB = "github"
    DARK = "dark"
    LIGHT = "light"
    QUANTUM = "quantum"


class StateVisualizer:
    """Visualizer for quantum states with GitHub Octocat theming."""
    
    # GitHub Colors
    GITHUB_COLORS = {
        'black': '#24292e',
        'white': '#ffffff',
        'gray': '#6a737d',
        'blue': '#0366d6',
        'green': '#2cbe4e',
        'red': '#d73a49',
        'purple': '#6f42c1',
        'yellow': '#ffdf5d',
        'octocat': '#f5f5f5'
    }
    
    def __init__(self, 
                style: VisualizationStyle = VisualizationStyle.GITHUB,
                dark_mode: bool = False):
        """Initialize the state visualizer.
        
        Args:
            style: Visualization style
            dark_mode: Whether to use dark mode
        """
        self.style = style
        self.dark_mode = dark_mode
        self.logger = logging.getLogger(__name__)
        
        # Set up style
        self._setup_style()
        
    def _setup_style(self) -> None:
        """Set up the visualization style."""
        if self.style == VisualizationStyle.GITHUB:
            # GitHub Octocat theme
            if self.dark_mode:
                self.colors = {
                    'background': '#0d1117',
                    'text': '#f0f6fc',
                    'primary': '#58a6ff',
                    'secondary': '#8b949e',
                    'accent': '#f78166',
                    'grid': '#30363d',
                    'bloch_sphere': '#8b949e',
                    'probability': '#58a6ff',
                    'phase': '#f78166',
                    'positive': '#2ea043',
                    'negative': '#f85149'
                }
            else:
                self.colors = {
                    'background': '#ffffff',
                    'text': '#24292e',
                    'primary': '#0366d6',
                    'secondary': '#6a737d',
                    'accent': '#d73a49',
                    'grid': '#e1e4e8',
                    'bloch_sphere': '#e1e4e8',
                    'probability': '#0366d6',
                    'phase': '#d73a49',
                    'positive': '#2cbe4e',
                    'negative': '#d73a49'
                }
        elif self.style == VisualizationStyle.DARK:
            # Dark theme
            self.colors = {
                'background': '#121212',
                'text': '#ffffff',
                'primary': '#bb86fc',
                'secondary': '#03dac6',
                'accent': '#cf6679',
                'grid': '#333333',
                'bloch_sphere': '#333333',
                'probability': '#bb86fc',
                'phase': '#03dac6',
                'positive': '#03dac6',
                'negative': '#cf6679'
            }
        elif self.style == VisualizationStyle.LIGHT:
            # Light theme
            self.colors = {
                'background': '#ffffff',
                'text': '#121212',
                'primary': '#6200ee',
                'secondary': '#03dac6',
                'accent': '#b00020',
                'grid': '#e0e0e0',
                'bloch_sphere': '#e0e0e0',
                'probability': '#6200ee',
                'phase': '#018786',
                'positive': '#018786',
                'negative': '#b00020'
            }
        elif self.style == VisualizationStyle.QUANTUM:
            # Quantum-inspired theme
            self.colors = {
                'background': '#040438',
                'text': '#e0f7fa',
                'primary': '#4fc3f7',
                'secondary': '#9575cd',
                'accent': '#f06292',
                'grid': '#3f51b5',
                'bloch_sphere': '#3f51b5',
                'probability': '#4fc3f7',
                'phase': '#f06292',
                'positive': '#64ffda',
                'negative': '#ff4081'
            }
        else:
            # Standard theme
            self.colors = {
                'background': '#ffffff',
                'text': '#000000',
                'primary': '#1f77b4',
                'secondary': '#ff7f0e',
                'accent': '#d62728',
                'grid': '#cccccc',
                'bloch_sphere': '#cccccc',
                'probability': '#1f77b4',
                'phase': '#ff7f0e',
                'positive': '#2ca02c',
                'negative': '#d62728'
            }
            
        # Apply style
        plt.style.use('default')
        plt.rcParams['figure.facecolor'] = self.colors['background']
        plt.rcParams['axes.facecolor'] = self.colors['background']
        plt.rcParams['text.color'] = self.colors['text']
        plt.rcParams['axes.labelcolor'] = self.colors['text']
        plt.rcParams['xtick.color'] = self.colors['text']
        plt.rcParams['ytick.color'] = self.colors['text']
        plt.rcParams['axes.edgecolor'] = self.colors['grid']
        plt.rcParams['axes.grid'] = True
        plt.rcParams['grid.color'] = self.colors['grid']
        plt.rcParams['grid.alpha'] = 0.3
        
    def plot_statevector(self, 
                       statevector: Union[np.ndarray, 'Statevector'],
                       title: Optional[str] = None,
                       figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
        """Plot the amplitude and phase of a statevector.
        
        Args:
            statevector: State vector to visualize
            title: Title for the plot
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        try:
            # Convert to numpy array if needed
            if hasattr(statevector, 'data'):
                sv_data = statevector.data
            else:
                sv_data = statevector
                
            # Get probabilities and phases
            probabilities = np.abs(sv_data) ** 2
            phases = np.angle(sv_data)
            
            # Create figure
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
            fig.patch.set_facecolor(self.colors['background'])
            
            # Plot probabilities
            bar_positions = np.arange(len(probabilities))
            bar_width = 0.7
            ax1.bar(bar_positions, probabilities, 
                   color=self.colors['probability'],
                   width=bar_width,
                   edgecolor=self.colors['grid'],
                   alpha=0.8)
            
            # Format probability plot
            ax1.set_ylim(0, 1)
            ax1.set_xlabel('Basis State')
            ax1.set_ylabel('Probability')
            ax1.set_title('State Probabilities')
            
            # Add basis state labels
            num_qubits = int(np.log2(len(probabilities)))
            if num_qubits <= 5:  # Only show binary labels for small systems
                basis_labels = [format(i, f'0{num_qubits}b') for i in range(len(probabilities))]
                ax1.set_xticks(bar_positions)
                ax1.set_xticklabels(basis_labels, rotation=70)
            else:
                ax1.set_xticks(bar_positions[::max(1, len(probabilities)//10)])
                
            # Add GitHub Octocat icon for the highest probability state if GitHub style
            if self.style == VisualizationStyle.GITHUB:
                max_idx = np.argmax(probabilities)
                octocat_icon = self._get_octocat_icon()
                if octocat_icon is not None:
                    octocat_position = (max_idx, probabilities[max_idx] + 0.05)
                    octocat_size = max(0.05, min(0.15, 1.0 / len(probabilities) * 10))
                    if octocat_position[1] < 0.95:  # Ensure the icon fits
                        ax1.imshow(octocat_icon, extent=[octocat_position[0]-octocat_size/2, 
                                                       octocat_position[0]+octocat_size/2, 
                                                       octocat_position[1], 
                                                       octocat_position[1]+octocat_size], 
                                 aspect='auto', zorder=10, alpha=0.9)
            
            # Plot phases
            ax2.bar(bar_positions, phases,
                   color=self.colors['phase'],
                   width=bar_width,
                   edgecolor=self.colors['grid'],
                   alpha=0.8)
            
            # Format phase plot
            ax2.set_ylim(-np.pi, np.pi)
            ax2.set_xlabel('Basis State')
            ax2.set_ylabel('Phase (radians)')
            ax2.set_title('State Phases')
            
            # Add basis state labels
            if num_qubits <= 5:
                ax2.set_xticks(bar_positions)
                ax2.set_xticklabels(basis_labels, rotation=70)
            else:
                ax2.set_xticks(bar_positions[::max(1, len(probabilities)//10)])
                
            # Add horizontal lines at 0, π, and -π
            ax2.axhline(y=0, color=self.colors['grid'], linestyle='-', alpha=0.5)
            ax2.axhline(y=np.pi, color=self.colors['grid'], linestyle='--', alpha=0.5)
            ax2.axhline(y=-np.pi, color=self.colors['grid'], linestyle='--', alpha=0.5)
            
            # Add labels for π and -π
            ax2.text(-0.5, np.pi, '$\\pi$', color=self.colors['text'], va='center')
            ax2.text(-0.5, -np.pi, '$-\\pi$', color=self.colors['text'], va='center')
            
            # Add main title
            if title:
                fig.suptitle(title, fontsize=16)
                
            fig.tight_layout()
            return fig
            
        except Exception as e:
            self.logger.error(f"Error plotting statevector: {str(e)}")
            # Return an error figure
            fig = plt.figure(figsize=(8, 6))
            fig.patch.set_facecolor(self.colors['background'])
            plt.text(0.5, 0.5, f"Error: {str(e)}", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=plt.gca().transAxes,
                   color=self.colors['accent'])
            return fig
            
    def plot_bloch_vector(self, 
                         state: Union[np.ndarray, 'Statevector'],
                         qubit_indices: Optional[List[int]] = None,
                         title: Optional[str] = None) -> plt.Figure:
        """Plot the Bloch vector representation of qubits.
        
        Args:
            state: Quantum state to visualize
            qubit_indices: Indices of qubits to visualize
            title: Title for the plot
            
        Returns:
            Matplotlib figure
        """
        try:
            # Convert to Statevector if needed
            if isinstance(state, np.ndarray):
                state = Statevector(state)
                
            # Determine number of qubits
            num_qubits = int(np.log2(len(state)))
            
            # Default to all qubits if indices not specified
            if qubit_indices is None:
                qubit_indices = list(range(min(num_qubits, 5)))  # Limit to 5 qubits by default
                
            # Ensure we don't exceed the number of qubits
            qubit_indices = [i for i in qubit_indices if i < num_qubits]
            
            # Create plot
            num_plots = len(qubit_indices)
            if num_plots == 0:
                return None
                
            # Calculate grid layout
            cols = min(3, num_plots)
            rows = (num_plots + cols - 1) // cols
            
            # Create figure
            fig = plt.figure(figsize=(4*cols, 4*rows))
            fig.patch.set_facecolor(self.colors['background'])
            
            # Add title
            if title:
                fig.suptitle(title, fontsize=16)
            
            # Create Bloch spheres for each qubit
            for i, qubit in enumerate(qubit_indices):
                # Get reduced density matrix for the qubit
                rho = state.partial_trace([q for q in range(num_qubits) if q != qubit])
                
                # Create Bloch sphere
                ax = fig.add_subplot(rows, cols, i+1, projection='3d')
                ax.set_facecolor(self.colors['background'])
                
                # Create Bloch sphere
                sphere = Bloch(axes=ax)
                
                # Style the Bloch sphere
                sphere.frame_color = self.colors['text']
                sphere.sphere_color = self.colors['bloch_sphere']
                sphere.sphere_alpha = 0.1
                sphere.point_color = [self.colors['primary']]
                sphere.font_color = self.colors['text']
                sphere.vector_color = [self.colors['primary']]
                
                # Calculate Bloch vector
                bloch_vector = [np.real(rho[1][0] + rho[0][1]),  # x
                               np.imag(rho[0][1] - rho[1][0]),  # y
                               np.real(rho[0][0] - rho[1][1])]  # z
                
                # Add vector to Bloch sphere
                sphere.add_vectors(bloch_vector)
                
                # Add GitHub Octocat point if GitHub style
                if self.style == VisualizationStyle.GITHUB:
                    # Add a small Octocat at the end of the vector
                    sphere.point_marker = 'o'
                    sphere.point_size = 20
                
                # Set title
                sphere.title = f'Qubit {qubit}'
                
                # Render the Bloch sphere
                sphere.render()
                
            fig.tight_layout()
            return fig
            
        except Exception as e:
            self.logger.error(f"Error plotting Bloch vector: {str(e)}")
            # Return an error figure
            fig = plt.figure(figsize=(8, 6))
            fig.patch.set_facecolor(self.colors['background'])
            plt.text(0.5, 0.5, f"Error: {str(e)}", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=plt.gca().transAxes,
                   color=self.colors['accent'])
            return fig
            
    def plot_histogram(self, 
                     counts: Dict[str, int],
                     title: Optional[str] = None,
                     figsize: Tuple[int, int] = (10, 6)) -> plt.Figure:
        """Plot a histogram of measurement results.
        
        Args:
            counts: Dictionary of measurement counts
            title: Title for the plot
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        try:
            # Create figure
            fig, ax = plt.subplots(figsize=figsize)
            fig.patch.set_facecolor(self.colors['background'])
            
            # Sort by binary value
            sorted_counts = sorted(counts.items(), key=lambda x: int(x[0], 2) if x[0].isdigit() else x[0])
            labels = [item[0] for item in sorted_counts]
            values = [item[1] for item in sorted_counts]
            
            # Create bars
            bar_positions = np.arange(len(values))
            bar_width = 0.7
            
            # If GitHub-themed, use color gradient based on probability
            if self.style == VisualizationStyle.GITHUB:
                # Create color gradient from secondary to primary color
                max_value = max(values)
                norm_values = [v / max_value for v in values]
                
                # Create bars with gradient colors
                for i, (val, norm_val) in enumerate(zip(values, norm_values)):
                    color = self._color_blend(self.colors['secondary'], 
                                            self.colors['primary'], 
                                            norm_val)
                    ax.bar(bar_positions[i], val, width=bar_width, color=color, 
                         edgecolor=self.colors['grid'], alpha=0.8)
                    
                # Add GitHub Octocat icon for the highest probability state
                max_idx = np.argmax(values)
                octocat_icon = self._get_octocat_icon()
                if octocat_icon is not None:
                    octocat_position = (max_idx, values[max_idx] * 1.05)
                    octocat_size = max(0.05, min(0.15, 1.0 / len(values) * 10))
                    if octocat_position[1] < values[max_idx] * 1.2:  # Ensure the icon fits
                        ax.imshow(octocat_icon, extent=[octocat_position[0]-octocat_size/2, 
                                                     octocat_position[0]+octocat_size/2, 
                                                     octocat_position[1], 
                                                     octocat_position[1]+octocat_size*values[max_idx]/10], 
                               aspect='auto', zorder=10, alpha=0.9)
            else:
                # Create bars with single color
                ax.bar(bar_positions, values, width=bar_width, 
                     color=self.colors['primary'], 
                     edgecolor=self.colors['grid'], alpha=0.8)
            
            # Format plot
            ax.set_xlabel('Bitstring')
            ax.set_ylabel('Counts')
            if title:
                ax.set_title(title)
                
            # Format x-axis
            ax.set_xticks(bar_positions)
            if len(labels) <= 16:
                ax.set_xticklabels(labels, rotation=70)
            else:
                # If too many labels, show fewer
                step = max(1, len(labels) // 16)
                shown_positions = bar_positions[::step]
                shown_labels = labels[::step]
                ax.set_xticks(shown_positions)
                ax.set_xticklabels(shown_labels, rotation=70)
            
            # Add grid
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels on top of bars if not too many
            if len(values) <= 20:
                for i, v in enumerate(values):
                    ax.text(i, v + (max(values) * 0.01), str(v), 
                          ha='center', va='bottom', 
                          color=self.colors['text'],
                          fontsize=8)
                          
            fig.tight_layout()
            return fig
            
        except Exception as e:
            self.logger.error(f"Error plotting histogram: {str(e)}")
            # Return an error figure
            fig = plt.figure(figsize=(8, 6))
            fig.patch.set_facecolor(self.colors['background'])
            plt.text(0.5, 0.5, f"Error: {str(e)}", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=plt.gca().transAxes,
                   color=self.colors['accent'])
            return fig
            
    def plot_entanglement_graph(self, 
                              adjacency_matrix: np.ndarray, 
                              entanglement_strengths: Optional[np.ndarray] = None,
                              qubit_labels: Optional[List[str]] = None,
                              title: Optional[str] = None,
                              figsize: Tuple[int, int] = (8, 8)) -> plt.Figure:
        """Plot the entanglement graph between qubits.
        
        Args:
            adjacency_matrix: Matrix representing connections between qubits
            entanglement_strengths: Matrix of entanglement strengths (optional)
            qubit_labels: Labels for the qubits
            title: Title for the plot
            figsize: Figure size
            
        Returns:
            Matplotlib figure
        """
        try:
            # Import networkx if available
            import networkx as nx
            
            # Create graph from adjacency matrix
            G = nx.from_numpy_array(adjacency_matrix)
            
            # Create figure
            fig, ax = plt.subplots(figsize=figsize)
            fig.patch.set_facecolor(self.colors['background'])
            ax.set_facecolor(self.colors['background'])
            
            # Generate layout
            pos = nx.spring_layout(G)
            
            # Default node labels if not provided
            if qubit_labels is None:
                qubit_labels = [f"Q{i}" for i in range(len(adjacency_matrix))]
                
            # Create edge widths based on entanglement strengths
            if entanglement_strengths is not None:
                edge_widths = []
                for u, v in G.edges():
                    edge_widths.append(2 * entanglement_strengths[u, v])
            else:
                edge_widths = [2 for _ in G.edges()]
                
            # Draw nodes
            node_size = 1000 if len(G.nodes) <= 10 else 500
            
            # For GitHub theme, use Octocat-like coloring
            if self.style == VisualizationStyle.GITHUB:
                # Draw edges with gradient color based on entanglement strength
                if entanglement_strengths is not None:
                    for (u, v) in G.edges():
                        strength = entanglement_strengths[u, v]
                        color = self._color_blend(self.colors['secondary'], 
                                               self.colors['primary'], 
                                               strength)
                        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], 
                                            width=2*strength, 
                                            edge_color=color,
                                            alpha=0.7,
                                            ax=ax)
                else:
                    nx.draw_networkx_edges(G, pos, width=edge_widths, 
                                         edge_color=self.colors['primary'],
                                         alpha=0.7,
                                         ax=ax)
                                         
                # Draw nodes with Octocat coloring
                node_colors = [self.colors['accent'] if i == 0 else self.colors['primary'] 
                             for i in range(len(G.nodes))]
                nx.draw_networkx_nodes(G, pos, 
                                     node_size=node_size,
                                     node_color=node_colors,
                                     edgecolors=self.colors['grid'],
                                     linewidths=2,
                                     alpha=0.8,
                                     ax=ax)
                                     
                # Add Octocat icon to the center of the graph if possible
                octocat_icon = self._get_octocat_icon()
                if octocat_icon is not None:
                    center_x = sum(xy[0] for xy in pos.values()) / len(pos)
                    center_y = sum(xy[1] for xy in pos.values()) / len(pos)
                    icon_size = 0.2
                    ax.imshow(octocat_icon, extent=[center_x-icon_size/2, 
                                                  center_x+icon_size/2, 
                                                  center_y-icon_size/2, 
                                                  center_y+icon_size/2], 
                            zorder=0, alpha=0.3)
            else:
                # Standard drawing
                nx.draw_networkx_edges(G, pos, width=edge_widths, 
                                     edge_color=self.colors['primary'],
                                     alpha=0.7,
                                     ax=ax)
                nx.draw_networkx_nodes(G, pos, 
                                     node_size=node_size,
                                     node_color=self.colors['primary'],
                                     edgecolors=self.colors['grid'],
                                     linewidths=2,
                                     alpha=0.8,
                                     ax=ax)
            
            # Add labels
            label_dict = {i: label for i, label in enumerate(qubit_labels)}
            nx.draw_networkx_labels(G, pos, labels=label_dict, 
                                  font_color=self.colors['text'],
                                  font_size=10,
                                  ax=ax)
            
            # Add title
            if title:
                ax.set_title(title)
                
            # Remove axis
            ax.set_axis_off()
            
            return fig
            
        except ImportError:
            self.logger.error("NetworkX not available for entanglement graph visualization")
            # Return a simple matrix visualization instead
            fig, ax = plt.subplots(figsize=figsize)
            fig.patch.set_facecolor(self.colors['background'])
            
            if entanglement_strengths is not None:
                matrix = entanglement_strengths
            else:
                matrix = adjacency_matrix
                
            im = ax.imshow(matrix, cmap='viridis', interpolation='nearest')
            fig.colorbar(im, label='Entanglement')
            
            # Set ticks and labels
            if qubit_labels is not None:
                ax.set_xticks(np.arange(len(qubit_labels)))
                ax.set_yticks(np.arange(len(qubit_labels)))
                ax.set_xticklabels(qubit_labels)
                ax.set_yticklabels(qubit_labels)
                
            # Add grid
            ax.grid(False)
            
            # Add title
            if title:
                ax.set_title(title)
                
            return fig
        except Exception as e:
            self.logger.error(f"Error plotting entanglement graph: {str(e)}")
            # Return an error figure
            fig = plt.figure(figsize=(8, 6))
            fig.patch.set_facecolor(self.colors['background'])
            plt.text(0.5, 0.5, f"Error: {str(e)}", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=plt.gca().transAxes,
                   color=self.colors['accent'])
            return fig
            
    def plot_circuit(self, 
                   circuit: 'QuantumCircuit',
                   title: Optional[str] = None) -> Any:
        """Plot a quantum circuit with GitHub Octocat theme.
        
        Args:
            circuit: Quantum circuit to visualize
            title: Title for the plot
            
        Returns:
            Circuit visualization object
        """
        try:
            # Use qiskit's built-in drawer with custom style
            from qiskit.visualization import circuit_drawer
            
            # Apply styling
            style = {
                'name': 'github' if self.style == VisualizationStyle.GITHUB else 'default',
                'textcolor': self.colors['text'],
                'gatetextcolor': self.colors['text'],
                'subtextcolor': self.colors['secondary'],
                'linecolor': self.colors['text'],
                'creglinecolor': self.colors['secondary'],
                'gatefacecolor': self.colors['primary'],
                'barrierfacecolor': self.colors['secondary'],
                'backgroundcolor': self.colors['background'],
                'bold': True
            }
            
            # Draw the circuit
            fig = circuit_drawer(circuit, output='mpl', style=style)
            
            # Add title if provided
            if title:
                fig.suptitle(title, fontsize=16, y=0.95)
                
            return fig
            
        except Exception as e:
            self.logger.error(f"Error plotting circuit: {str(e)}")
            # Return an error figure
            fig = plt.figure(figsize=(8, 6))
            fig.patch.set_facecolor(self.colors['background'])
            plt.text(0.5, 0.5, f"Error: {str(e)}", 
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=plt.gca().transAxes,
                   color=self.colors['accent'])
            return fig
            
    def _color_blend(self, color1: str, color2: str, ratio: float) -> str:
        """Blend two colors based on a ratio.
        
        Args:
            color1: First color (hex format)
            color2: Second color (hex format)
            ratio: Blending ratio (0.0 to 1.0)
            
        Returns:
            Blended color (hex format)
        """
        # Convert hex to RGB
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        # Blend colors
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
        
    def _get_octocat_icon(self) -> Optional[np.ndarray]:
        """Get the GitHub Octocat icon as a numpy array.
        
        Returns:
            Numpy array representing the Octocat icon, or None if not available
        """
        try:
            # Simple ASCII art representation of the Octocat
            octocat_ascii = [
                "    *****    ",
                "   *******   ",
                "  *********  ",
                " *** *** *** ",
                " ***********" ,
                " ***********" ,
                "  *********  ",
                "   *******   ",
                "    *****    "
            ]
            
            # Convert ASCII art to image array
            height = len(octocat_ascii)
            width = max(len(line) for line in octocat_ascii)
            image = np.zeros((height, width, 4))
            
            # Fill in the image
            for i, line in enumerate(octocat_ascii):
                for j, char in enumerate(line):
                    if char == '*':
                        if self.dark_mode:
                            image[i, j, :] = [1.0, 1.0, 1.0, 1.0]  # White in dark mode
                        else:
                            image[i, j, :] = [0.0, 0.0, 0.0, 1.0]  # Black in light mode
                    else:
                        image[i, j, :] = [0.0, 0.0, 0.0, 0.0]  # Transparent
            
            return image
            
        except Exception as e:
            self.logger.error(f"Error creating Octocat icon: {str(e)}")
            return None
            
    def figure_to_base64(self, fig: plt.Figure) -> Optional[str]:
        """Convert a matplotlib figure to base64 encoding.
        
        Args:
            fig: Matplotlib figure
            
        Returns:
            Base64-encoded string, or None if conversion failed
        """
        try:
            # Save figure to a buffer
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            
            # Convert to base64
            img_str = base64.b64encode(buf.read()).decode('utf-8')
            
            return img_str
            
        except Exception as e:
            self.logger.error(f"Error converting figure to base64: {str(e)}")
            return None
            
    def save_figure(self, fig: plt.Figure, filename: str) -> bool:
        """Save a figure to a file.
        
        Args:
            fig: Matplotlib figure
            filename: Filename to save to
            
        Returns:
            True if save successful, False otherwise
        """
        try:
            fig.savefig(filename, bbox_inches='tight')
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving figure: {str(e)}")
            return False