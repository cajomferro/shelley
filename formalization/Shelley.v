Require Import Coq.Strings.String.
Require Import Coq.Lists.List.
Import ListNotations.
Definition trace := list string.
Open Scope string.


Ltac invc X := inversion X; subst; clear X. 

Module Imp.
Inductive t :=
  | call (func: string) : t
  | skip: t
  | ret : t
  | seq (fst:t) (snd:t)
  | branch (then_branch:t) (else_branch:t) : t
  | loop (body:t) : t
  .

  Module In.
    Inductive status := Halt | Running.
    Inductive t:  Imp.t -> trace -> status -> Prop :=
    | call:
      forall x,
      t (Imp.call x) [x] Running
    | skip:
      t Imp.skip [] Running
    | ret:
      t Imp.ret [] Halt
    | seq_l:
      forall p1 p2 l,
      t p1 l Halt ->
      t (Imp.seq p1 p2) l Halt
    | seq_r:
      forall p1 p2 l1 l2 s,
      t p1 l1 Running ->
      t p2 l2 s ->
      t (Imp.seq p1 p2) (List.app l1 l2) s
    | branch_l:
      forall p1 p2 l s,
      t p1 l s ->
      t (Imp.branch p1 p2) l s
    | branch_r:
      forall p1 p2 l s,
      t p2 l s ->
      t (Imp.branch p1 p2) l s
    | loop_end:
      forall p,
      t (Imp.loop p) [] Running
    | loop_halt:
      forall p l,
      t p l Halt ->
      t (Imp.loop p) l Halt
    | loop_unroll:
      forall l1 l2 p s,
      t p l1 Running ->
      t (Imp.loop p) l2 s ->
      t (Imp.loop p) (List.app l1 l2) s.

  Lemma loop_1:
    forall p l s,
    t p l s ->
    t (loop p) l s.
  Proof.
    intros.
    destruct s. {
      apply loop_halt.
      assumption.
    }
    assert (t (loop p) (List.app l []) Running). {
      apply loop_unroll; auto.
      apply loop_end.
    }
    rewrite app_nil_r in *.
    assumption.
  Qed.

  Lemma loop_unroll_rev:
    forall p l1,
    t (Imp.loop p) l1 Running ->
    forall  l2 s,
    t p l2 s ->
    t (Imp.loop p) (List.app l1 l2) s.
  Proof.
    intros p l1 H.
    remember (loop _) as q.
    generalize dependent p.
    remember Running as s.
    generalize dependent Heqs.
    induction H.
    all: intros heq1 q heq2 l2' s' hr.
    all: invc heq2.
    - simpl.
      apply loop_1.
      assumption.
    - invc heq1.
    - assert (IHt2 := IHt2 eq_refl _ eq_refl).
      assert (IHt1 := IHt1 eq_refl).
      rewrite <- app_assoc.
      apply loop_unroll; auto.
  Qed.
  End In.
End Imp.

Module Regex.
Inductive t :=
  | concat (fst:t) (snd:t)
  | or (fst:t) (snd:t)
  | star (body:t)
  | epsilon
  | void
  | char (value:string).

  Definition or_list (l: list t) : t :=
    List.fold_left or l void.

  Module In.
    Inductive t : trace -> Regex.t -> Prop :=
    | char:
      forall x,
      t [x] (Regex.char x)
    | epsilon:
      t [] (Regex.epsilon)
    | star_nil:
      forall r,
      t [] (Regex.star r)
    | star_app:
      forall l1 l2 r,
      t l1 r ->
      t l2 (Regex.star r) ->
      t (List.app l1 l2) (Regex.star r)
    | or_l:
      forall r1 r2 l,
      t l r1 ->
      t l (Regex.or r1 r2)
    | or_r:
      forall r1 r2 l,
      t l r2 ->
      t l (Regex.or r1 r2)
    | concat:
      forall r1 r2 l1 l2,
      t l1 r1 ->
      t l2 r2 ->
      t (List.app l1 l2) (Regex.concat r1 r2).

    Lemma fold_left_or_base:
      forall l w r,
      t w r ->
      t w (fold_left or l r).
    Proof.
      induction l; intros. {
        simpl.
        assumption.
      }
      simpl.
      apply IHl.
      apply or_l.
      assumption.
    Qed.

    Lemma fold_left_or_step:
      forall l w r,
      List.In r l ->
      t w r ->
      forall r',
      t w (fold_left or l r').
    Proof.
      induction l; intros. {
        contradiction.
      }
      simpl in H.
      intuition. {
        subst.
        simpl.
        apply fold_left_or_base.
        apply or_r.
        assumption.
      }
      simpl.
      eapply IHl; eauto.
    Qed.

    Lemma inv_fold_left_or:
      forall w l r,
      t w (fold_left or l r) ->
      t w r \/ exists r', List.In r' l /\ t w r'.
    Proof.
      induction l; intros. {
        simpl in *.
        intuition.
      }
      simpl in *.
      apply IHl in H.
      intuition. {
        invc H0; intuition.
        right.
        exists a.
        intuition.
      }
      right.
      destruct H0 as (r', (Hi, Hr)).
      eauto.
    Qed. 

  End In.

  Fixpoint to_string (r:t) : string :=
    match r with
    | concat r1 r2 =>
      to_string r1 ++ "; " ++ to_string r2
    | or r1 r2 =>
      "{ " ++ to_string r1 ++ " } + { " ++ to_string r2 ++ " }"
    | star r =>
      "loop { " ++ to_string r ++ " }"
    | epsilon => ""
    | void => "VOID"
    | char x => x
    end. 

  Fixpoint cleanup (r:t) : t :=
    match r with
    | concat r1 r2 =>
      match cleanup r1, cleanup r2 with
      | void, _ | _, void => void
      | epsilon, r | r, epsilon => r
      | r1, r2 => concat r1 r2
      end
    | or r1 r2 =>
      match cleanup r1, cleanup r2 with
      | void, r | r, void => r
      | r1, r2 => or r1 r2
      end
    | star r =>
      match r with
      | void | epsilon => epsilon
      | star r | r => star r
      end
    | _ => r
    end.
End Regex.

Definition prepend (r:Regex.t) (l:list Regex.t) : list Regex.t :=
  List.map (Regex.concat r) l.

  Fixpoint translate (p:Imp.t) : (Regex.t * list Regex.t) :=
  match p with
  | Imp.call f => (Regex.char f, [])
  | Imp.ret => (Regex.void, [Regex.epsilon])
  | Imp.skip => (Regex.epsilon, [])
  | Imp.seq p1 p2 =>
    let (r1, l1) := translate p1 in
    let (r2, l2) := translate p2 in
    (Regex.concat r1 r2, List.app l1 (prepend r1 l2))
  | Imp.branch p1 p2 =>
    let (r1, l1) := translate p1 in
    let (r2, l2) := translate p2 in
    (Regex.or r1 r2, List.app l1 l2)
  | Imp.loop p =>
    let (r, l) := translate p in
    (Regex.star r, prepend (Regex.star r) l) 
  end.

Lemma sound_1:
  forall l p,
  Imp.In.t p l Imp.In.Running ->
  Regex.In.t l (fst (translate p)).
Proof.
  intros l p H.
  remember Imp.In.Running as s.
  induction H.
  all: simpl.
  all: try invc Heqs.
  - constructor.
  - constructor.
  - destruct (translate p1) as (r1, l_r1) eqn:heq1.
    destruct (translate p2) as (r2, l_r2) eqn:heq2.
    simpl.
    constructor.
    all: auto.
  - destruct (translate p1) as (r1, l_r1) eqn:heq1.
    destruct (translate p2) as (r2, l_r2) eqn:heq2.
    simpl.
    apply Regex.In.or_l.
    auto.
  - destruct (translate p1) as (r1, l_r1) eqn:heq1.
    destruct (translate p2) as (r2, l_r2) eqn:heq2.
    simpl.
    destruct s. { invc Heqs. }
    apply Regex.In.or_r.
    auto.
  - destruct (translate p) as (r, l_r) eqn:heq1.
    simpl.
    constructor.
  - subst.
    destruct (translate p) as (r, l_r) eqn:heq1.
    simpl.
    assert (IHt1 := IHt1 eq_refl).
    assert (IHt2 := IHt2 eq_refl).
    simpl in *.
    rewrite heq1 in *.
    simpl in *.
    apply Regex.In.star_app; eauto.
Qed.

Lemma in_prepend:
  forall l r1 r2,
  In r2 l ->
  In (Regex.concat r1 r2) (prepend r1 l).
Proof.
  intros.
  unfold prepend.
  rewrite in_map_iff.
  exists r2.
  intuition.
Qed.

Lemma in_inv_prepend:
  forall r r1 l,
  In r (prepend r1 l) ->
  exists r2, r = Regex.concat r1 r2 /\ List.In r2 l.
Proof.
  unfold prepend.
  intros.
  rewrite in_map_iff in *.
  destruct H as (r', (?, ?)).
  eauto.
Qed.

Lemma sound_2:
  forall l p,
  Imp.In.t p l Imp.In.Halt ->
  exists r, List.In r (snd (translate p)) /\ Regex.In.t l r.
Proof.
  intros l p H.
  remember Imp.In.Halt as s.
  induction H.
  all: try invc Heqs.
  all: simpl.
  all: try destruct (translate p1) as (r1, l_r1) eqn:heq1.
  all: try destruct (translate p2) as (r2, l_r2) eqn:heq2.
  all: try destruct (translate p) as (r, l_r) eqn:heq1.
  - exists Regex.epsilon.
    intuition.
    constructor.
  - assert (IHt := IHt eq_refl).
    destruct IHt as (r', (Hi, Hr)).
    simpl in *.
    exists r'.
    split; auto.
    rewrite in_app_iff.
    intuition.
  - subst.
    clear IHt1.
    assert (IHt2 := IHt2 eq_refl).
    destruct IHt2 as (r', (Hi, Hr')).
    simpl in *.
    exists (Regex.concat r1 r').
    split. {
      rewrite in_app_iff.
      eauto using in_prepend.
    }
    apply Regex.In.concat; auto.
    apply sound_1 in H.
    rewrite heq1 in *.
    simpl in *.
    assumption.
  - subst.
    assert (IHt := IHt eq_refl).
    destruct IHt as (r, (Hi, Hr')).
    simpl in *.
    exists r.
    split; auto.
    rewrite in_app_iff.
    intuition.
  - subst.
    assert (IHt := IHt eq_refl).
    destruct IHt as (r, (Hi, Hr')).
    simpl in *.
    exists r.
    split; auto.
    rewrite in_app_iff.
    intuition.
  - assert (IHt := IHt eq_refl).
    destruct IHt as (r', (Hi, Hr')).
    simpl in *.
    exists (Regex.concat (Regex.star r) r').
    split. {
      eauto using in_prepend.
    }
    assert (Regex.In.t (List.app [] l) (Regex.concat (Regex.star r) r')). {
      constructor.
      + constructor.
      + assumption.
    }
    assumption.
  - subst.
    clear IHt1.
    assert (IHt2 := IHt2 eq_refl).
    destruct IHt2 as (r', (Hi, Hr')).
    simpl in Hi.
    rewrite heq1 in Hi.
    simpl in *.
    apply sound_1 in H.
    rewrite heq1 in H.
    simpl in *.
    apply in_inv_prepend in Hi.
    destruct Hi as (r2, (Heq, Hi)).
    subst.
    invc Hr'.
    exists (Regex.concat (Regex.star r) r2).
    split. {
      apply in_prepend.
      assumption.
    }
    rewrite app_assoc.
    constructor; auto.
    apply Regex.In.star_app; auto.
Qed.

  Definition infer r : Regex.t :=
    let (r, l) := translate r in
    List.fold_left Regex.or l r.


  Definition Outputs l p :=
    exists s, Imp.In.t p l s.


Theorem sound:
  forall l p,
  Outputs l p ->
  Regex.In.t l (infer p).
Proof.
  intros.
  destruct H as ([], Hi).
  - apply sound_2 in Hi.
    destruct Hi as (r, (Hi, Hj)).
    unfold infer.
    destruct (translate p) as (r1, l1).
    simpl in *.
    eapply Regex.In.fold_left_or_step; eauto.
  - apply sound_1 in Hi.
    unfold infer.
    destruct (translate p) as (r1, l1).
    simpl in *.
    eapply Regex.In.fold_left_or_base; eauto.
Qed.

Lemma complete_1:
  forall l p,
  Regex.In.t l (fst (translate p)) ->
  Imp.In.t p l Imp.In.Running.
Proof.
  intros l p H.
  remember (fst _) as x.
  generalize dependent p.
  induction H.
  all: intros p Heq.
  all: destruct p.
  all: invc Heq.
  all: try (constructor; auto; fail).
  all: try destruct (translate p1) as (r1', l_r1) eqn:heq1.
  all: try destruct (translate p2) as (r2', l_r2) eqn:heq2.
  all: try destruct (translate p) as (r1', l_r1) eqn:heq1.
  all: simpl in *.
  all: try match goal with H: Regex.char _ = _ |- _ => invc H end.
  all: try match goal with H: Regex.epsilon = _ |- _ => invc H end.
  all: try match goal with H: Regex.star _ = _ |- _ => invc H end.
  all: try match goal with H: Regex.or _  _ = _ |- _ => invc H end.
  all: try match goal with H: Regex.concat _  _ = _ |- _ => invc H end.
  - assert (IHt2 := IHt2 (Imp.loop p)).
    simpl in IHt2.
    rewrite heq1 in IHt2.
    simpl in IHt2.
    assert (IHt2 := IHt2 eq_refl).
    specialize IHt1 with p.
    rewrite heq1 in *.
    simpl in IHt1.
    assert (IHt1 := IHt1 eq_refl).
    apply Imp.In.loop_unroll; auto.
  - specialize IHt with p1.
    rewrite heq1 in *.
    assert (IHt := IHt eq_refl).
    apply Imp.In.branch_l.
    assumption.
  - specialize IHt with p2.
    rewrite heq2 in *.
    assert (IHt := IHt eq_refl).
    apply Imp.In.branch_r.
    assumption.
  - specialize IHt1 with p1.
    specialize IHt2 with p2.
    rewrite heq1 in *.
    rewrite heq2 in *.
    assert (IHt1 := IHt1 eq_refl).
    assert (IHt2 := IHt2 eq_refl).
    apply Imp.In.seq_r; auto.
Qed.

Lemma complete_2:
  forall p l r,
  List.In r (snd (translate p)) ->
  Regex.In.t l r ->
  Imp.In.t p l Imp.In.Halt.
Proof.
  induction p.
  all: intros l r hi hr.
  - simpl in *.
    contradiction.
  - simpl in *.
    contradiction.
  - simpl in *.
    intuition.
    subst.
    invc hr.
    constructor.
  - simpl in hi.
    destruct (translate p1) as (r1, l_r1) eqn:heq1.
    destruct (translate p2) as (r2, l_r2) eqn:heq2.
    simpl in hi.
    rewrite in_app_iff in hi.
    destruct hi as [hi|hi]. {
      apply Imp.In.seq_l.
      eapply IHp1; eauto.
    }
    apply in_inv_prepend in hi.
    destruct hi as (r2', (?, hi)).
    subst.
    invc hr.
    apply Imp.In.seq_r.
    + apply complete_1.
      rewrite heq1.
      simpl.
      assumption.
    + eauto.
  - simpl in hi.
    destruct (translate p1) as (r1, l_r1) eqn:heq1.
    destruct (translate p2) as (r2, l_r2) eqn:heq2.
    simpl in hi.
    rewrite in_app_iff in hi.
    destruct hi as [hi|hi]. {
      apply Imp.In.branch_l.
      eapply IHp1; eauto.
    }
    apply Imp.In.branch_r.
    eapply IHp2; eauto.
  - simpl in hi.
    destruct (translate p) as (r', l_r) eqn:heq1.
    simpl in hi.
    apply in_inv_prepend in hi.
    destruct hi as (r2, (?, hi)).
    subst.
    invc hr.
    simpl in IHp.
    apply IHp with (l:=l2) in hi; auto.
    clear IHp.
    assert (Hx := complete_1 l1 (Imp.loop p)).
    simpl in Hx.
    rewrite heq1 in Hx.
    simpl in Hx.
    apply Hx in H2.
    clear Hx.
    auto using Imp.In.loop_unroll_rev.
Qed.

Lemma complete:
  forall l p,
  Regex.In.t l (infer p) ->
  Outputs l p.
Proof.
  unfold infer.
  intros.
  destruct (translate p) as (r', l') eqn:eq1.
  apply Regex.In.inv_fold_left_or in H.
  destruct H as [H|(r, (Hi, Hr))]. {
    exists Imp.In.Running.
    apply complete_1.
    rewrite eq1.
    assumption.
  }
  exists Imp.In.Halt.
  eapply complete_2; eauto.
  rewrite eq1.
  assumption.
Qed.

Corollary correct:
  forall l p,
  Regex.In.t l (infer p) <-> Outputs l p.
Proof.
  split; auto using sound, complete.
Qed.

