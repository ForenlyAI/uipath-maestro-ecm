import React from 'react';
import { motion } from 'framer-motion';
import { ServerOff, TrendingDown, ShieldAlert } from 'lucide-react';

const AnimatedCards: React.FC = () => {
  const cards = [
    {
      title: 'Idle GPU Waste',
      description: 'Teams waste thousands of dollars leaving expensive cloud GPUs running after training ends.',
      icon: ServerOff,
      color: 'text-red-500',
      bg: 'from-red-500/10 to-transparent'
    },
    {
      title: 'Silent Divergence',
      description: 'Training silently collapses. Rewards flatten. Gradients vanish. Nobody notices until hours later.',
      icon: TrendingDown,
      color: 'text-orange-500',
      bg: 'from-orange-500/10 to-transparent'
    },
    {
      title: 'No Governance',
      description: 'There is no unified system for AI analysis, human approvals, robotic execution, and compliance auditing.',
      icon: ShieldAlert,
      color: 'text-yellow-500',
      bg: 'from-yellow-500/10 to-transparent'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {cards.map((card, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: idx * 0.2 }}
          className={`glass-panel p-8 rounded-2xl relative overflow-hidden group hover:border-white/30 transition duration-300`}
        >
          <div className={`absolute inset-0 bg-gradient-to-b ${card.bg} opacity-0 group-hover:opacity-100 transition duration-500`}></div>
          <div className="relative z-10">
            <div className={`w-14 h-14 rounded-full bg-white/5 flex items-center justify-center mb-6 border border-white/10 ${card.color}`}>
              <card.icon className="w-7 h-7" />
            </div>
            <h3 className="text-2xl font-bold text-white mb-4">{card.title}</h3>
            <p className="text-gray-400 leading-relaxed">
              {card.description}
            </p>
          </div>
        </motion.div>
      ))}
    </div>
  );
};

export default AnimatedCards;
