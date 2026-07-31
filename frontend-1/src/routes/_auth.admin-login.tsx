import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, ShieldAlert } from 'lucide-react';
import { supabase } from '@/lib/supabase';
import { toast } from 'sonner';

export const Route = createFileRoute('/_auth/admin-login')({
  component: AdminLogin,
});

function AdminLogin() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please enter email and password');
      return;
    }
    
    setLoading(true);
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;
      
      // Before letting them proceed, double check if they are actually an admin
      // We will check the email directly to bypass any database permission issues
      if (data.user.email !== 'spoorthipyadav@gmail.com' && data.user.email !== 'spoorthi2615@gmail.com') {
        // They are a normal user trying to use the admin login. Kick them out.
        await supabase.auth.signOut();
        toast.error('Unauthorized access', { description: 'You do not have administrative privileges.' });
        return;
      }

      // Log the admin login activity
      supabase.from('activity_logs').insert([
        { user_id: data.user.id, action: 'Admin securely authenticated' }
      ]).then();

      toast.success('Admin access granted');
      navigate({ to: '/admin' });
    } catch (error: any) {
      toast.error('Login failed', { description: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4">
      <div className="flex flex-col gap-2 text-center">
        <div className="mx-auto mb-2 flex h-12 w-12 items-center justify-center rounded-full bg-destructive/10 text-destructive">
          <ShieldAlert className="h-6 w-6" />
        </div>
        <h1 className="text-2xl font-semibold tracking-tight text-destructive">Restricted Access</h1>
        <p className="text-sm text-muted-foreground">
          This portal is for AgileGraph administrators only.
        </p>
      </div>
      
      <form onSubmit={handleAdminLogin} className="flex flex-col gap-4">
        <div className="grid gap-2">
          <Label htmlFor="email">Admin Email</Label>
          <Input 
            id="email" 
            type="email" 
            placeholder="admin@agilegraph.io" 
            required 
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>
        <div className="grid gap-2">
          <div className="flex items-center">
            <Label htmlFor="password">Password</Label>
          </div>
          <Input 
            id="password" 
            type="password" 
            placeholder="••••••••" 
            required 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        
        <Button type="submit" variant="destructive" className="w-full" disabled={loading}>
          {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
          Secure Login
        </Button>
      </form>
    </div>
  );
}
