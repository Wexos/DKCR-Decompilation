#pragma once

#include "Game/CRenderActor.h"

class CCollisionInfoList;
class CCollisionPrimitive;
class CStateManager;
class TUniqueId;

class CPhysicsActor : public CRenderActor
{
public:
    ~CPhysicsActor() override;
    
    bool TypesMatch(int) const override;
    void AcceptScriptMsg(CStateManager&, const CScriptMsg&) override;    
    void DoUserAnimEvent(CStateManager&, const CAnimUserNotify&, NAnim::EEventState, f32) override;
    virtual bool WillMove(const CStateManager&) const;
    virtual const CCollisionPrimitive* GetCollisionPrimitive() const;
    virtual void GetPrimitiveTransform() const;
    virtual void GetCollisionResolutionResponse(const CStateManager&, const TUniqueId&) const;
    virtual void CollidedWith(CStateManager&, const TUniqueId&, const CCollisionInfoList&);
    virtual f32 GetWeight() const;
};
