'use client';

import { motion } from 'framer-motion';

export default function MeshBackdrop() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none select-none">
      {/* Mesh Gradient Container */}
      <div className="mesh-backdrop" />
      
      {/* Animated Floating Blobs */}
      <motion.div
        animate={{
          x: [0, 100, 0],
          y: [0, -50, 0],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute top-1/4 left-1/4 w-[500px] h-[500px] bg-egret-accent/10 rounded-full blur-[120px]"
      />
      <motion.div
        animate={{
          x: [0, -150, 0],
          y: [0, 100, 0],
          scale: [1, 1.3, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute bottom-1/4 right-1/4 w-[600px] h-[600px] bg-egret-secondary/10 rounded-full blur-[140px]"
      />
    </div>
  );
}
